import logging
from datetime import date

import stripe
from django.db import DatabaseError, IntegrityError, transaction

from accounts.models import User
from checkout.models import Order, Service
from checkout.tasks import order_confirmation_mail
from projects.models import Project

logger = logging.getLogger(__name__)


def fulfill_checkout(session_id):
    """
    Processes a successful Stripe Checkout session and fulfills the Order.

    This function ensures that each Order is only processed once and safely
    creates the corresponding Project.

    Workflow:
        - Called from both success page view and Stripe webhook.
        - Uses database transactions with row locking for safety.
        - Returns None on error to indicate that processing is incomplete,
            allowing the success view to display an appropriate message to the
            user. Errors are logged so the Order can be processed manually if
            needed. Returns a new Project instance on success so that the success
            view can display Project details.
        - Send confirmation e-mail (Celery task) to the user on success.
        - Return existing Project if the Order has already been filled.

    Returns:
        Project: The created Project instance on success.
        None: On processing failure or invalid session.
    """
    try:
        session = stripe.checkout.Session.retrieve(
            session_id,
        )
    except stripe.StripeError as e:
        logger.error(
            f"Checkout fulfillment error (Stripe session error)"
            f"Session: {session_id}. Error: {e}"
        )

    if session.payment_status != "paid":
        return None

    try:
        order_pk = session["metadata"]["order_pk"]
        user_id = session["metadata"]["user_id"]
    except KeyError as e:
        logger.error(
            f"Checkout fulfillment error (missing metadata). "
            f"Session: {session_id}. Error: {e}"
        )
        return None

    try:
        with transaction.atomic():
            # Lock associated rows
            user = User.objects.select_for_update().get(pk=user_id)
            order = Order.objects.select_for_update().get(
                pk=order_pk, user=user
            )

            if order.order_processed:
                return order.project

            if order.service.package_type == Service.PackageType.SEO_STRATEGY:
                new_project = Project.objects.create(
                    service=order.service,
                    project_name=order.project_name,
                    website=order.website,
                    description=order.additional_info,
                    keywords=order.keywords,
                    competitor=order.competitor,
                )

                new_project.admin.add(user)
                new_project.members.add(user)

                order.order_processed = True
                order.order_processed_date = date.today()
                order.project = new_project
                order.save()

                order_confirmation_mail.delay(new_project.pk)
                return new_project

            elif (
                order.service.package_type
                == Service.PackageType.LINK_BUILDING_STRATEGY
            ):
                # TODO
                return None

            elif order.service.package_type == Service.PackageType.KEYWORD:
                # TODO
                return None

    except (User.DoesNotExist, Order.DoesNotExist) as e:
        logger.error(
            f"Checkout fulfillment error (user / order not found)."
            f"Session: {session_id}. Error: {e}"
        )
        return None

    except (IntegrityError, DatabaseError) as e:
        logger.error(
            f"Checkout fulfillment error (database). "
            f"Session: {session_id}. Error: {e}"
        )
        return None
