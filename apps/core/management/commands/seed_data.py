from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed the database with initial sample data'

    def add_arguments(self, parser):
        parser.add_argument('--flush', action='store_true', help='Flush existing data before seeding')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        self._seed_salon_settings()
        self._seed_opening_hours()
        self._seed_service_categories()
        self._seed_services()
        self._seed_team()
        self._seed_gallery_categories()
        self._seed_faqs()
        self._seed_testimonials()
        self._seed_blog_categories()
        self.stdout.write(self.style.SUCCESS('Database seeded successfully.'))

    def _flush(self):
        from apps.core.models import SalonSettings, OpeningHours, ContactMessage
        from apps.services.models import ServiceCategory, Service, Promotion
        from apps.team.models import Stylist
        from apps.gallery.models import GalleryCategory, GalleryImage
        from apps.testimonials.models import Testimonial
        from apps.faqs.models import FAQCategory, FAQ
        from apps.blog.models import BlogCategory, BlogPost

        for model in [ContactMessage, Testimonial, FAQ, FAQCategory, BlogPost, BlogCategory,
                      GalleryImage, GalleryCategory, Stylist, Service, Promotion,
                      ServiceCategory, OpeningHours, SalonSettings]:
            model.objects.all().delete()
        self.stdout.write('Existing data flushed.')

    def _seed_salon_settings(self):
        from apps.core.models import SalonSettings
        SalonSettings.objects.update_or_create(
            pk=1,
            defaults={
                'salon_name': 'Balirah Beauty Salon',
                'tagline': 'Where Style Meets Elegance — Kampala\'s Premier Barber & Nails Studio',
                'about_short': (
                    'Balirah Beauty Salon is Kampala\'s most sought-after destination for precision '
                    'barbering and luxury nail services. We combine craft with luxury to give you '
                    'an experience that goes beyond a haircut.'
                ),
                'phone_primary': '+256 700 000 001',
                'phone_secondary': '+256 700 000 002',
                'email': 'hello@balirahsalon.com',
                'address': 'Plot 12, Acacia Avenue, Kololo, Kampala, Uganda',
                'whatsapp_number': '+256700000001',
                'meta_title': 'Balirah Beauty Salon – Barber & Nails in Kampala',
                'meta_description': (
                    'Premium barbering and nail services in Kampala, Uganda. '
                    'Book your appointment online today.'
                ),
            }
        )
        self.stdout.write('  Salon settings seeded.')

    def _seed_opening_hours(self):
        from apps.core.models import OpeningHours
        from datetime import time

        hours = [
            (0, time(8, 0), time(20, 0), False),
            (1, time(8, 0), time(20, 0), False),
            (2, time(8, 0), time(20, 0), False),
            (3, time(8, 0), time(20, 0), False),
            (4, time(8, 0), time(21, 0), False),
            (5, time(8, 0), time(21, 0), False),
            (6, time(9, 0), time(17, 0), False),
        ]
        for day, open_t, close_t, closed in hours:
            OpeningHours.objects.update_or_create(
                day=day,
                defaults={'open_time': open_t, 'close_time': close_t, 'is_closed': closed}
            )
        self.stdout.write('  Opening hours seeded.')

    def _seed_service_categories(self):
        from apps.services.models import ServiceCategory

        categories = [
            {'name': 'Barber Services', 'slug': 'barber-services', 'category_type': 'barber',
             'icon': 'fa-cut', 'order': 1,
             'description': 'Precision cuts and grooming for the modern man.'},
            {'name': 'Nail Services', 'slug': 'nail-services', 'category_type': 'nails',
             'icon': 'fa-spa', 'order': 2,
             'description': 'Luxury nail care and artistry for hands and feet.'},
            {'name': 'Combo Packages', 'slug': 'combo-packages', 'category_type': 'combo',
             'icon': 'fa-star', 'order': 3,
             'description': 'The best of both worlds — grooming and nails in one visit.'},
        ]
        for data in categories:
            ServiceCategory.objects.update_or_create(slug=data['slug'], defaults=data)
        self.stdout.write('  Service categories seeded.')

    def _seed_services(self):
        from apps.services.models import Service, ServiceCategory

        barber = ServiceCategory.objects.get(slug='barber-services')
        nails = ServiceCategory.objects.get(slug='nail-services')
        combo = ServiceCategory.objects.get(slug='combo-packages')

        services = [
            {'category': barber, 'name': 'Classic Haircut', 'slug': 'classic-haircut',
             'description': 'Precision scissor or clipper cut tailored to your face shape and style.',
             'short_description': 'Clean, sharp, tailored cut.',
             'price': 15000, 'duration_minutes': 30, 'is_featured': True, 'order': 1,
             'reengagement_category': 'haircut'},
            {'category': barber, 'name': 'Haircut & Beard Trim', 'slug': 'haircut-beard-trim',
             'description': 'Full haircut combined with a precision beard shape and trim.',
             'short_description': 'Complete hair and beard grooming.',
             'price': 25000, 'duration_minutes': 45, 'is_featured': True, 'order': 2,
             'reengagement_category': 'haircut'},
            {'category': barber, 'name': 'Hot Towel Shave', 'slug': 'hot-towel-shave',
             'description': 'Traditional straight-razor shave with hot towel treatment and aftershave.',
             'short_description': 'The classic barber experience.',
             'price': 20000, 'duration_minutes': 40, 'is_featured': True, 'order': 3,
             'reengagement_category': 'beard'},
            {'category': barber, 'name': 'Beard Sculpt & Shape', 'slug': 'beard-sculpt-shape',
             'description': 'Expert beard sculpting, edge-up, and conditioning treatment.',
             'short_description': 'Define and perfect your beard.',
             'price': 15000, 'duration_minutes': 30, 'is_featured': False, 'order': 4,
             'reengagement_category': 'beard'},
            {'category': barber, 'name': 'Kids Haircut', 'slug': 'kids-haircut',
             'description': 'Gentle and fun haircut for children under 12.',
             'short_description': 'Fun cuts for the little ones.',
             'price': 10000, 'duration_minutes': 25, 'is_featured': False, 'order': 5,
             'reengagement_category': 'haircut'},
            {'category': barber, 'name': 'Fade & Design', 'slug': 'fade-design',
             'description': 'Custom skin fade with creative hair design or pattern.',
             'short_description': 'Art meets barbering.',
             'price': 30000, 'price_max': 45000, 'duration_minutes': 60, 'is_featured': True, 'order': 6,
             'reengagement_category': 'haircut'},
            {'category': nails, 'name': 'Classic Manicure', 'slug': 'classic-manicure',
             'description': 'Nail shaping, cuticle care, buff and polish for natural nails.',
             'short_description': 'Clean, polished, natural nails.',
             'price': 25000, 'duration_minutes': 45, 'is_featured': True, 'order': 1,
             'reengagement_category': 'nails'},
            {'category': nails, 'name': 'Gel Manicure', 'slug': 'gel-manicure',
             'description': 'Long-lasting gel colour application with UV curing and glossy finish.',
             'short_description': 'Two-week shine guarantee.',
             'price': 40000, 'duration_minutes': 60, 'is_featured': True, 'order': 2,
             'reengagement_category': 'nails'},
            {'category': nails, 'name': 'Acrylic Full Set', 'slug': 'acrylic-full-set',
             'description': 'Full acrylic nail extension set with shape, length and colour of your choice.',
             'short_description': 'Length, strength, and style.',
             'price': 70000, 'price_max': 100000, 'duration_minutes': 90, 'is_featured': True, 'order': 3,
             'reengagement_category': 'nails'},
            {'category': nails, 'name': 'Classic Pedicure', 'slug': 'classic-pedicure',
             'description': 'Foot soak, scrub, nail shaping, cuticle care and polish.',
             'short_description': 'Happy, healthy feet.',
             'price': 35000, 'duration_minutes': 60, 'is_featured': False, 'order': 4,
             'reengagement_category': 'nails'},
            {'category': nails, 'name': 'Nail Art Design', 'slug': 'nail-art-design',
             'description': 'Custom nail art, patterns, gems, or decals on any nail service.',
             'short_description': 'Express yourself with nail art.',
             'price': 15000, 'price_max': 40000, 'duration_minutes': 30, 'is_featured': False, 'order': 5,
             'reengagement_category': 'nails'},
            {'category': combo, 'name': 'The Full Works', 'slug': 'the-full-works',
             'description': 'Haircut, beard trim, and classic manicure — total grooming in one session.',
             'short_description': 'Head-to-hand grooming package.',
             'price': 60000, 'duration_minutes': 105, 'is_featured': True, 'order': 1,
             'reengagement_category': 'default'},
            {'category': combo, 'name': 'Date Night Package', 'slug': 'date-night-package',
             'description': 'Haircut, hot towel shave, and gel manicure to look your absolute best.',
             'short_description': 'Look sharp for any occasion.',
             'price': 75000, 'duration_minutes': 120, 'is_featured': True, 'order': 2,
             'reengagement_category': 'default'},
        ]
        for data in services:
            Service.objects.update_or_create(
                slug=data['slug'],
                defaults={k: v for k, v in data.items() if k != 'slug'}
            )
        self.stdout.write('  Services seeded.')

    def _seed_team(self):
        from apps.team.models import Stylist
        from apps.services.models import ServiceCategory

        barber_cat = ServiceCategory.objects.get(slug='barber-services')
        nails_cat = ServiceCategory.objects.get(slug='nail-services')

        members = [
            {'first_name': 'Brian', 'last_name': 'Ssemanda', 'slug': 'brian-ssemanda',
             'role': 'barber', 'years_experience': 8, 'order': 1,
             'bio': 'Brian is a master barber with 8 years of experience in precision fades, classic cuts and beard sculpting. His eye for detail and passion for the craft make him the go-to stylist for discerning clients.',
             'specializations': [barber_cat]},
            {'first_name': 'David', 'last_name': 'Ochieng', 'slug': 'david-ochieng',
             'role': 'barber', 'years_experience': 5, 'order': 2,
             'bio': 'David specialises in modern cuts, hair designs and hot towel shaves. His calm demeanour and creative flair consistently deliver results clients love.',
             'specializations': [barber_cat]},
            {'first_name': 'Grace', 'last_name': 'Nakato', 'slug': 'grace-nakato',
             'role': 'nail_tech', 'years_experience': 6, 'order': 3,
             'bio': 'Grace is a certified nail technician who transforms nails into works of art. From classic manicures to intricate nail art, her precision and creativity are unmatched.',
             'specializations': [nails_cat]},
            {'first_name': 'Irene', 'last_name': 'Atim', 'slug': 'irene-atim',
             'role': 'nail_tech', 'years_experience': 4, 'order': 4,
             'bio': 'Irene brings warmth and expertise to every nail appointment. She excels in gel, acrylic and pedicure services and keeps up with the latest trends.',
             'specializations': [nails_cat]},
            {'first_name': 'Moses', 'last_name': 'Kiggundu', 'slug': 'moses-kiggundu',
             'role': 'both', 'years_experience': 10, 'order': 5,
             'bio': 'Moses is Balirah\'s most versatile stylist. With a decade of experience across barbering and nail care, he leads with mastery, mentorship and meticulous attention to every client.',
             'specializations': [barber_cat, nails_cat]},
        ]
        for data in members:
            specs = data.pop('specializations')
            stylist, _ = Stylist.objects.update_or_create(
                slug=data['slug'],
                defaults={k: v for k, v in data.items() if k != 'slug'}
            )
            stylist.specializations.set(specs)
        self.stdout.write('  Team seeded.')

    def _seed_gallery_categories(self):
        from apps.gallery.models import GalleryCategory

        categories = [
            {'name': 'Haircuts', 'slug': 'haircuts', 'order': 1},
            {'name': 'Beard & Shave', 'slug': 'beard-shave', 'order': 2},
            {'name': 'Nails', 'slug': 'nails', 'order': 3},
            {'name': 'Before & After', 'slug': 'before-after', 'order': 4},
        ]
        for data in categories:
            GalleryCategory.objects.update_or_create(slug=data['slug'], defaults=data)
        self.stdout.write('  Gallery categories seeded.')

    def _seed_faqs(self):
        from apps.faqs.models import FAQCategory, FAQ

        general, _ = FAQCategory.objects.update_or_create(name='General', defaults={'order': 1})
        booking, _ = FAQCategory.objects.update_or_create(name='Bookings', defaults={'order': 2})
        services_cat, _ = FAQCategory.objects.update_or_create(name='Services', defaults={'order': 3})

        faqs = [
            (general, 'Where is Balirah Beauty Salon located?',
             'We are located at Plot 12, Acacia Avenue, Kololo, Kampala, Uganda. You can find us on Google Maps or WhatsApp us for directions.', 1),
            (general, 'What are your opening hours?',
             'We are open Monday to Friday 8 AM–8 PM, Saturday 8 AM–9 PM, and Sunday 9 AM–5 PM.', 2),
            (general, 'Do you accept walk-ins?',
             'Yes, we welcome walk-ins subject to availability. However, we strongly recommend booking online to guarantee your preferred time slot and stylist.', 3),
            (booking, 'How do I book an appointment?',
             'You can book directly on our website by selecting your service, preferred stylist, date and time. You can also WhatsApp or call us to book.', 1),
            (booking, 'Can I cancel or reschedule my appointment?',
             'Yes. You can cancel or reschedule up to 2 hours before your appointment time through your account profile or by contacting us on WhatsApp.', 2),
            (booking, 'Will I receive a confirmation after booking?',
             'Yes. You will receive an SMS and email confirmation immediately after booking, plus reminders 24 hours and 2 hours before your appointment.', 3),
            (services_cat, 'How long does a haircut take?',
             'A standard haircut takes 25–45 minutes. Fades with designs can take up to 60 minutes. Service duration is shown on the booking page.', 1),
            (services_cat, 'Do you use quality products?',
             'Absolutely. We use only professional-grade products from trusted brands to ensure the best results and protect your hair and skin.', 2),
            (services_cat, 'Do you offer nail extensions for men?',
             'We offer nail grooming and buffing for men as part of our combo packages. Full nail extensions are available for all clients.', 3),
        ]
        for category, question, answer, order in faqs:
            FAQ.objects.update_or_create(
                question=question,
                defaults={'category': category, 'answer': answer, 'order': order, 'is_active': True}
            )
        self.stdout.write('  FAQs seeded.')

    def _seed_testimonials(self):
        from apps.testimonials.models import Testimonial
        from apps.services.models import Service

        try:
            haircut = Service.objects.get(slug='classic-haircut')
            fade = Service.objects.get(slug='fade-design')
            gel = Service.objects.get(slug='gel-manicure')
            acrylic = Service.objects.get(slug='acrylic-full-set')
            full_works = Service.objects.get(slug='the-full-works')
        except Service.DoesNotExist:
            self.stdout.write(self.style.WARNING('  Services not found, skipping testimonials.'))
            return

        testimonials = [
            ('Kampala John', haircut, 5, 'Best barber experience in Kampala hands down. Brian understood exactly what I wanted and the cut was flawless. Will not go anywhere else.', True),
            ('Sarah Nakayima', gel, 5, 'Grace is an absolute artist! My gel nails lasted three full weeks without chipping. The salon atmosphere is luxurious and the staff are so welcoming.', True),
            ('Derrick Mugisha', fade, 5, 'David\'s fades are on another level. Clean lines, perfect blend, and the design he added was exactly what I had in mind. Book this man!', True),
            ('Priscilla Aber', acrylic, 5, 'I had my acrylic set done by Irene and I am obsessed. She was patient with my design ideas and the result was beyond what I expected.', True),
            ('Alex Tumwesigye', full_works, 5, 'Got the Full Works package and it was worth every shilling. Haircut, beard trim and manicure all in one visit. I left feeling like a completely new person.', True),
            ('Ruth Apio', gel, 4, 'Very professional service and clean salon. Grace took her time to make sure I loved the colour before applying. Highly recommend for nail services.', True),
        ]
        for name, service, rating, body, featured in testimonials:
            Testimonial.objects.get_or_create(
                client_name=name,
                defaults={
                    'service': service, 'rating': rating, 'body': body,
                    'is_approved': True, 'is_featured': featured,
                }
            )
        self.stdout.write('  Testimonials seeded.')

    def _seed_blog_categories(self):
        from apps.blog.models import BlogCategory

        categories = ['Hair Care', 'Beard Grooming', 'Nail Trends', 'Style Tips', 'Salon News']
        for name in categories:
            from django.utils.text import slugify
            BlogCategory.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
        self.stdout.write('  Blog categories seeded.')
