const stripe = Stripe(STRIPE_PK);

initialize();

// Create a Checkout Session
async function initialize() {
  const fetchClientSecret = async () => {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const response = await fetch("/checkout/checkout-session/", {
      method: "POST",
      headers: { "Content-Type": "application/json", 'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({
        price_id: PRICE_ID,
        order_pk: ORDER_PK
      }),
    });
    const { clientSecret } = await response.json();
    return clientSecret;
  };

  const checkout = await stripe.initEmbeddedCheckout({
    fetchClientSecret,
  });

  // Mount Checkout
  checkout.mount('#checkout');
}