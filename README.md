# BrandishSEO Demo
![BrandishSEO](https://github.com/dorian-adams/BrandishSEO-Demo/blob/main/brandishSEO-home.jpg)

## Overview
This repo is the public version of a private repo and is for demonstration purposes to showcase some of the core aspects of my first Django project. Please, feel free to view the website itself at, [BrandishSEO.com](https://brandishseo.com).

## What is BrandishSEO?
BrandishSEO is a search marketing company specializing in comprehensive SEO strategies for small businesses. BrandishSEO leverages technology in unique ways to make strategy implementation faster and easier.

## Technologies
The following technologies are utilized in this project:
* Python 3
* Django 4.1
* Wagtail 4.0.2
* BeautifulSoup 4
* Whitenoise 6.2
* AWS CloudFront CDN
* PostgreSQL
* Stripe
* Bootstrap
* Node.js and Grunt for uncss

## Purpose
The primary purpose behind BrandishSEO is to combine my ten years of experience as an SEO analyst with my newfound knowledge of programming to create a platform that makes SEO more accessible and easier to implement.

## What I Learned
In working on this project, I gained valuable first-hand experience with many core aspects of Django development. Including class-based views, function-based views, creating mix-ins for DRY, forms, storage, custom user models, ORM, Python scripting, authentication, performance optimization, deployment, and more. Most importantly, I developed this project from idea to deployment. In doing so, I learned how to work through challenges, debug, and see a project to completion. 

## Development at a Glance
Development highlights:
* Developed a customer portal, which also acts as a project management platform. Allows clients to invite coworkers to their team, assign tasks, track progress, and communicate efficiently from one centralized platform.
* Clients receive their SEO strategy as a Word Document, which outlines all the tasks they must complete to improve their organic performance. Clients also have access to their customer portal, from which they can manage their projects. To save time, a Python script automatically parses the Word Document, extracts tasks, and creates `Task` objects while ignoring any supplementary information contained in the Doc. The script automatically runs via signals whenever the client's strategy is uploaded. So, the creation of tasks in the customer portal is entirely automated.
* Developed a script that analyzes the SEO of a given web page. The script currently analyzes the page's meta titles, descriptions, h1 tags, and links and reports back with any optimization opportunities. However, many more features are planned for the future. 
* Integrated Wagtail CMS for the blog.
* Ensured algorithms and heavy computational lifting reside in models, views, and scripts. Leaving as little computational work for the templates as possible.
* Multithreading is incorporated where appropriate. 
* Adhered to Django design principles to create a modular and easy-to-expand codebase.
