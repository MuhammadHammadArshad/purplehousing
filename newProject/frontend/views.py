from django.shortcuts import render, redirect, get_object_or_404
from .models import Blog
from .models import Booking, Property, Applying, CustomUser
from django.utils.dateparse import parse_date
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import os
from django.conf import settings
from django.core.paginator import Paginator
import json
from django.contrib import messages
from .decorators import login_required_custom
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import urlparse, parse_qs, urlencode


def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid username or password")
            return redirect(request.META.get("HTTP_REFERER", "dasboardIndex"))

        if user.is_active and user.check_password(password):
            # Login success, create session
            request.session["user_id"] = user.id
            request.session["username"] = user.username
            messages.success(request, f"Welcome {user.username}!")
            return redirect("dasboardIndex") 
        else:
            messages.error(request, "Invalid username or password")
            return redirect(request.META.get("HTTP_REFERER", "home"))

    return redirect("dasboardIndex")

def custom_logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully")
    return redirect("home")


def home(request):
    # return render(request, 'frontend/home.html')
       # Featured properties first
    featured_props = Property.objects.filter(featured=True).order_by('-id')
    other_props = Property.objects.filter(featured=False).order_by('-id')

    # Combine featured first
    props = list(featured_props) + list(other_props)

    blogs = Blog.objects.all().order_by('-id')[:5]


    # Limit to 6
    props = props[:6]

    return render(request, "frontend/home.html", {
        "MEDIA_URL": settings.MEDIA_URL,
        "properties": props,
        "blogs": blogs,

    })

def about(request):
    return render(request, 'frontend/about.html')

def contact(request):
    return render(request, 'frontend/contact.html')

def booking(request):
    return render(request, 'frontend/booking.html')

def property_details(request,property_id):
    # return render(request, 'frontend/property_details.html')
    property_obj = get_object_or_404(Property, id=property_id)
    context = {
        'property': property_obj,
        "MEDIA_URL": settings.MEDIA_URL,
    }
    return render(request, 'frontend/property_details.html', context )

def allProperties(request):
    # return render(request, 'frontend/properties.html')
    properties_list = Property.objects.all().order_by('-id')

    # Pagination: 9 properties per page
    paginator = Paginator(properties_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'frontend/properties.html', {
        "MEDIA_URL": settings.MEDIA_URL,
        'properties': page_obj,
    })

def applying(request):
    return render(request, 'frontend/applying.html')

def email_show(request):
    return render(request, 'frontend/email_show_template.html')

@login_required_custom
def dashboardListning(request):
    return render(request, 'dashboard/listning.html')

def thankyou(request):
    return render(request, 'frontend/thankyou.html')
def emailTemplate(request):
    return render(request, 'frontend/email_receive_tamplates.html')

# READ
@login_required_custom
def blog_list(request):
    blogs = Blog.objects.all()
    return render(request, "dashboard/blogs.html", {"blogs": blogs})

def blog_show(request):
    blogs = Blog.objects.all().order_by('-id')
    return render(request, "frontend/blog_show.html", {"blogs": blogs})

def blogs_details(request, id):
    blog = Blog.objects.get(id=id)
    return render(request, 'frontend/blog_details.html', {"blog": blog})

# CREATE
@login_required_custom
def blog_create(request):
    if request.method == "POST":
        # Create Blog instance safely
        blog = Blog(
            image=request.FILES.get("image"),
            title=request.POST.get("title"),
            description=request.POST.get("description"),
            keywords=request.POST.get("keywords"),
        )
        blog.save()  # save() method me WebP conversion handle ho raha hai

        # Redirect to blog list page
        return redirect("blog_list")  # Ensure your urls.py name="blog_list"

    return render(request, "dashboard/blog_create.html")

# UPDATE
@login_required_custom
def blog_update(request, pk):
    blog = get_object_or_404(Blog, pk=pk)

    if request.method == "POST":

        if request.FILES.get("image"):
            blog.image = request.FILES.get("image")

        blog.title = request.POST.get("title")
        blog.description = request.POST.get("description")
        blog.keywords = request.POST.get("keywords")
        blog.save()

        return redirect("blog_list")

    return render(request, "dashboard/blog_update.html", {"blog": blog})

# DELETE
def blog_delete(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    blog.delete()
    return redirect("blog_list")

# Booking schedule 

def create_booking(request):
    properties = Property.objects.filter(status='pending')
    if request.method == 'POST':
        property_name = request.POST.get('property')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        first_name = request.POST.get('fname')
        last_name = request.POST.get('lname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Convert date string to Python date
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            date = None

        if all([property_name, date, time_str, first_name, last_name, email, phone]):
            Booking.objects.create(
                property_name=property_name,
                date=date,
                time=time_str,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )

            return redirect('/thankyou/')

    return render(request, 'frontend/booking.html', {'properties': properties})

# Display Schedule
@login_required_custom
def schedule(request):
    bookings_list = Booking.objects.all().order_by('-id')
    paginator = Paginator(bookings_list, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    return render(request, 'dashboard/schedule.html', {'bookings': bookings})


@require_POST
def update_booking_status(request):
    booking_id = request.POST.get('id')
    status = request.POST.get('status')
    reason = request.POST.get('reason', '')
    
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = status
    if status == 'Disapproved':
        booking.reason = reason
    booking.save()
    
    return JsonResponse({'success': True, 'status': status})


#add proprty with list
# @login_required_custom
# def add_property(request):
#     if request.method == "POST":
#         # Create property instance
#         prop = Property.objects.create(
#             prop_title=request.POST.get('prop_title', ''),
#             prop_des=request.POST.get('prop_des', ''),
#             category=request.POST.get('category') or None,
#             purpose=request.POST.get('purpose') or None,
#             prop_price=request.POST.get('prop_price', '0'),
#             prop_beds=int(request.POST.get('prop_beds') or 0),
#             prop_baths=int(request.POST.get('prop_baths') or 0),
#             prop_size=request.POST.get('prop_size', '0'),
#             prop_year_built=request.POST.get('prop_year_built') or None,
#             property_map_address=request.POST.get('property_map_address', ''),
#             country=request.POST.get('country', ''),
#             administrative_area_level_1=request.POST.get('administrative_area_level_1', ''),
#             city=request.POST.get('locality', ''),
#             zip_code=request.POST.get('postal_code', ''),
#             lat=request.POST.get('lat', ''),
#             lng=request.POST.get('lng', ''),
#             prop_google_street_view=request.POST.get('prop_google_street_view', 'hide'),
#             featured=request.POST.get('prop_featured') == "1",
#             login_required=request.POST.get('login-required') == "1",
#             disclaimer=request.POST.get('property_disclaimer', ''),
#             status="pending"
#         )

#         # Save property features
#         prop.prop_features = request.POST.getlist('prop_features[]')

#         # === Save gallery images ===
#         images = request.FILES.getlist('gallery_images')
#         gallery_paths = []

#         for img in images[:10]:
#             timestamp = int(timezone.now().timestamp())
#             image_name = f"property_{prop.id}_{timestamp}_{img.name}"
#             image_path = os.path.join('property_images', image_name)
#             full_path = os.path.join(settings.MEDIA_ROOT, image_path)

#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as f:
#                 for chunk in img.chunks():
#                     f.write(chunk)

#             gallery_paths.append(image_path.replace("\\", "/"))

#         prop.gallery_images = gallery_paths

#         # === Save attachments ===
#         attachments = request.FILES.getlist('attachments')
#         attachments_paths = []

#         for file in attachments:
#             timestamp = int(timezone.now().timestamp())
#             file_name = f"property_{prop.id}_{timestamp}_{file.name}"
#             file_path = os.path.join('property_attachments', file_name)
#             full_path = os.path.join(settings.MEDIA_ROOT, file_path)

#             os.makedirs(os.path.dirname(full_path), exist_ok=True)
#             with open(full_path, 'wb+') as f:
#                 for chunk in file.chunks():
#                     f.write(chunk)

#             attachments_paths.append(file_path.replace("\\", "/"))

#         prop.attachments = attachments_paths

#         # Save everything
#         prop.save()

#         return redirect('dasboardIndex')

#     return render(request, "frontend/booking.html")

@login_required_custom
def add_property(request):
    if request.method == "POST":
        prop = Property.objects.create(
            prop_title=request.POST.get('prop_title', ''),
            prop_des=request.POST.get('prop_des', ''),
            category=request.POST.get('category') or None,
            purpose=request.POST.get('purpose') or None,
            prop_price=request.POST.get('prop_price', '0'),
            prop_beds=int(request.POST.get('prop_beds') or 0),
            prop_baths=int(request.POST.get('prop_baths') or 0),
            prop_size=request.POST.get('prop_size', '0'),
            prop_year_built=request.POST.get('prop_year_built') or None,
            property_map_address=request.POST.get('property_map_address', ''),
            country=request.POST.get('country', ''),
            administrative_area_level_1=request.POST.get('administrative_area_level_1', ''),
            city=request.POST.get('locality', ''),
            zip_code=request.POST.get('postal_code', ''),
            lat=request.POST.get('lat', ''),
            lng=request.POST.get('lng', ''),
            prop_google_street_view=request.POST.get('prop_google_street_view', 'hide'),
            featured=request.POST.get('prop_featured') == "1",
            login_required=request.POST.get('login-required') == "1",
            disclaimer=request.POST.get('property_disclaimer', ''),
            youtube_url=request.POST.get('youtube_url') or None,
            status="pending"
        )

        prop.prop_features = request.POST.getlist('prop_features[]')

        # ===== VIDEO FILE UPLOAD =====
        video = request.FILES.get('video_file')
        if video:
            timestamp = int(timezone.now().timestamp())
            video_name = f"property_video_{prop.id}_{timestamp}_{video.name}"
            video_path = os.path.join('property_videos', video_name)
            full_path = os.path.join(settings.MEDIA_ROOT, video_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb+') as f:
                for chunk in video.chunks():
                    f.write(chunk)

            prop.video_file = video_path.replace("\\", "/")

        # ===== GALLERY IMAGES (SAFE) =====
        images = request.FILES.getlist('gallery_images')
        featured_index = int(request.POST.get('featured_image', 0))
        gallery_paths = []

        for img in images[:10]:
            timestamp = int(timezone.now().timestamp())
            image_name = f"property_{prop.id}_{timestamp}_{img.name}"
            image_path = os.path.join('property_images', image_name)
            full_path = os.path.join(settings.MEDIA_ROOT, image_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb+') as f:
                for chunk in img.chunks():
                    f.write(chunk)

            gallery_paths.append(image_path.replace("\\", "/"))

        # ✅ FEATURED IMAGE LOGIC (OUTSIDE LOOP)
        if gallery_paths:
            if featured_index < 0 or featured_index >= len(gallery_paths):
                featured_index = 0

            featured_image = gallery_paths.pop(featured_index)
            gallery_paths.insert(0, featured_image)

            prop.featured_image = 0

        prop.gallery_images = gallery_paths

        # ===== ATTACHMENTS =====
        attachments = request.FILES.getlist('attachments')
        attachments_paths = []

        for file in attachments:
            timestamp = int(timezone.now().timestamp())
            file_name = f"property_{prop.id}_{timestamp}_{file.name}"
            file_path = os.path.join('property_attachments', file_name)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)

            attachments_paths.append(file_path.replace("\\", "/"))

        prop.attachments = attachments_paths
        prop.save()

        return redirect('dasboardIndex')

    return render(request, "frontend/booking.html")


@login_required_custom
def dasboardIndex(request):
    props = Property.objects.all().order_by('-id')
    paginator = Paginator(props, 10)  # Show 10 properties per page

    page_number = request.GET.get('page')  # Get page number from URL query
    page_obj = paginator.get_page(page_number)  # Handles invalid pages automatically
    return render(request, "dashboard/index.html", {
        # "properties": props,
        "MEDIA_URL": settings.MEDIA_URL,
        "page_obj": page_obj,
    })
    

@login_required_custom
def delete_property(request, pk):
    prop = Property.objects.get(id=pk)

    # gallery delete
    for img in prop.gallery_images:
        full_path = os.path.join(settings.MEDIA_ROOT, img)
        if os.path.exists(full_path):
            os.remove(full_path)

    # attachments delete
    for file in prop.attachments:
        full_path = os.path.join(settings.MEDIA_ROOT, file)
        if os.path.exists(full_path):
            os.remove(full_path)

    prop.delete()

    return redirect('dasboardIndex')

@login_required_custom
def update_property(request, pk):
    prop = Property.objects.get(id=pk)

    if request.method == "POST":

        # Basic fields update
        prop.prop_title = request.POST.get('prop_title', '')
        prop.prop_des = request.POST.get('prop_des', '')
        prop.category = request.POST.get('category') or None
        prop.purpose = request.POST.get('purpose') or None
        prop.prop_price = request.POST.get('prop_price', '0')
        prop.prop_beds = int(request.POST.get('prop_beds') or 0)
        prop.prop_baths = int(request.POST.get('prop_baths') or 0)
        prop.prop_size = request.POST.get('prop_size', '0')
        prop.prop_year_built = request.POST.get('prop_year_built') or None

        prop.property_map_address = request.POST.get('property_map_address', '')
        prop.country = request.POST.get('country', '')
        prop.administrative_area_level_1 = request.POST.get('administrative_area_level_1', '')
        prop.city = request.POST.get('locality', '')
        prop.zip_code = request.POST.get('postal_code', '')
        prop.lat = request.POST.get('lat', '')
        prop.lng = request.POST.get('lng', '')

        prop.featured = request.POST.get('prop_featured') == "1"
        prop.login_required = request.POST.get('login-required') == "1"
        prop.disclaimer = request.POST.get('property_disclaimer', '')
        prop.status = request.POST.get("status", "pending")

        # Features update
        prop.prop_features = request.POST.getlist('prop_features[]')

        new_images = request.FILES.getlist('gallery_images')

        if new_images:  
            # Purani images delete karein
            for img in prop.gallery_images:
                old_path = os.path.join(settings.MEDIA_ROOT, img)
                if os.path.exists(old_path):
                    os.remove(old_path)

            gallery_paths = []
            for img in new_images[:10]:
                timestamp = int(timezone.now().timestamp())
                image_name = f"property_{prop.id}_{timestamp}_{img.name}"
                image_path = os.path.join('property_images', image_name)
                full_path = os.path.join(settings.MEDIA_ROOT, image_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'wb+') as f:
                    for chunk in img.chunks():
                        f.write(chunk)

                gallery_paths.append(image_path.replace("\\", "/"))

            prop.gallery_images = gallery_paths

        new_files = request.FILES.getlist('attachments')

        if new_files:
            # Purane attachments delete
            for file_path in prop.attachments:
                old_path = os.path.join(settings.MEDIA_ROOT, file_path)
                if os.path.exists(old_path):
                    os.remove(old_path)

            attachment_paths = []
            for file in new_files:
                timestamp = int(timezone.now().timestamp())
                file_name = f"property_{prop.id}_{timestamp}_{file.name}"
                file_path = os.path.join('property_attachments', file_name)
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)

                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb+") as f:
                    for chunk in file.chunks():
                        f.write(chunk)

                attachment_paths.append(file_path.replace("\\", "/"))

            prop.attachments = attachment_paths

        prop.save()
        return redirect('dasboardIndex')

    return render(request, "dashboard/property_edit.html", {"prop": prop})

@require_POST
def expire_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    # Toggle status
    if prop.status == 'expire':
        prop.status = 'approved'   # Go Live
    else:
        prop.status = 'expire'     # Expire

    prop.save(update_fields=['status'])

    return JsonResponse({
        'status': prop.status
    })
# def expire_property(request, pk):
#     prop = get_object_or_404(Property, pk=pk)

#     if prop.status == 'expire':
#         prop.status = 'approved'   # go live
#     else:
#         prop.status = 'expire'     # expire

#     prop.save()

#     return JsonResponse({
#         'status': prop.status
#     })



@login_required_custom
def property_stats(request, pk):
    prop = get_object_or_404(Property, pk=pk)

    # attachments
    attachments = [{
        'url': f"{prop.MEDIA_URL}{file}" if hasattr(prop, 'MEDIA_URL') else f"/media/{file}",
        'name': os.path.basename(file)
    } for file in prop.attachments]

    # gallery images
    gallery_images = [f"{prop.MEDIA_URL}{img}" if hasattr(prop, 'MEDIA_URL') else f"/media/{img}" for img in prop.gallery_images]

    # local video
    video_url = f"{settings.MEDIA_URL}{prop.video_file}" if getattr(prop, 'video_file', None) else None

    # YouTube embed
    youtube_embed_url = None
    if prop.youtube_url:
        parsed_url = urlparse(prop.youtube_url)
        video_id = None

        # Normal watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        if 'youtube.com' in parsed_url.netloc and parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            video_id = query.get('v', [None])[0]

        # Short URL: https://youtu.be/VIDEO_ID
        elif 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.lstrip('/')

        # Shorts URL: https://www.youtube.com/shorts/VIDEO_ID
        elif 'youtube.com' in parsed_url.netloc and '/shorts/' in parsed_url.path:
            video_id = parsed_url.path.split('/')[-1]

        if video_id:
            # Construct **embed URL** safely with only the video_id
            youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"

    return render(request, 'dashboard/property_stats.html', {
        'prop': prop,
        'attachments': attachments,
        'gallery_images': gallery_images,
        'video_url': video_url,
        'youtube_embed_url': youtube_embed_url,
    })


#add applying
def add_application(request):
    properties = Property.objects.filter(status='pending')
    if request.method == "POST":
        # --- Helper functions ---
        def to_bool(value):
            return value == "on" or value == "true"

        def parse_date(value):
            if not value:
                return None
            try:
                # Convert MM/DD/YYYY to YYYY-MM-DD
                return datetime.strptime(value, "%m/%d/%Y").date()
            except ValueError:
                return None

        # --- Step 4 JSON fields ---
        adult_names = request.POST.getlist('adult_names[]')
        adult_emails = request.POST.getlist('adult_emails[]')
        adult_phones = request.POST.getlist('adult_phones[]')

        pet_details_raw = request.POST.get('pet_details', '[]')
        try:
            pet_details = json.loads(pet_details_raw)
        except json.JSONDecodeError:
            pet_details = []

        # --- Create Applying instance ---
        app = Applying.objects.create(
            # Step 1
            property_id=request.POST.get('property_id', ''),
            move_in_date=parse_date(request.POST.get('move_in_date')),
            applicant_type=request.POST.get('applicant_type'),

            # Step 2
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            email=request.POST.get('email', ''),
            confirm_email=request.POST.get('confirm_email', ''),
            phone=request.POST.get('phone', ''),
            hear_about=request.POST.get('hear_about', ''),

            # Step 3: Previous residence
            address1=request.POST.get('address1', ''),
            address2=request.POST.get('address2', ''),
            city=request.POST.get('city', ''),
            state=request.POST.get('state', ''),
            zipcode=request.POST.get('zipcode', ''),
            reside_from_month=request.POST.get('reside_from_month', ''),
            reside_from_year=request.POST.get('reside_from_year', ''),
            monthly_rent=request.POST.get('monthly_rent') or 0,
            monthly_mortgage=request.POST.get('monthly_mortgage') or 0,
            landlord_name=request.POST.get('landlord_name', ''),
            landlord_phone=request.POST.get('landlord_phone', ''),
            landlord_email=request.POST.get('landlord_email', ''),
            home_email=request.POST.get('home_email', ''),
            reason_for_leaving=request.POST.get('reason_for_leaving', ''),

            # Step 4: Housemates
            other_adults=to_bool(request.POST.get('other_adults')),
            adult_count=request.POST.get('adult_count') or 0,
            adult_names=adult_names,
            adult_emails=adult_emails,
            adult_phones=adult_phones,
            dependents_under_18=to_bool(request.POST.get('dependents_under_18')),
            dependent_first_name=request.POST.get('dependent_first_name', ''),
            dependent_last_name=request.POST.get('dependent_last_name', ''),
            dependent_relation=request.POST.get('dependent_relation', ''),
            dependent_dob=parse_date(request.POST.get('dependent_dob')),
            has_pets=to_bool(request.POST.get('has_pets')),
            pet_count=request.POST.get('pet_count') or 0,
            pet_details=pet_details,

            # Step 5: Personal info & vehicles
            dob=parse_date(request.POST.get('dob')),
            license_number=request.POST.get('license_number', ''),
            license_state=request.POST.get('license_state', ''),
            personal_email=request.POST.get('personal_email', ''),
            personal_phone=request.POST.get('personal_phone', ''),
            emergency_name=request.POST.get('emergency_name', ''),
            emergency_phone=request.POST.get('emergency_phone', ''),
            emergency_relation=request.POST.get('emergency_relation', ''),
            ssn=request.POST.get('ssn', ''),
            has_vehicle=to_bool(request.POST.get('has_vehicle')),
            vehicle_make=request.POST.get('vehicle_make', ''),
            vehicle_color=request.POST.get('vehicle_color', ''),
            vehicle_license=request.POST.get('vehicle_license', ''),
            vehicle_modal=request.POST.get('vehicle_modal', ''),
            vehicle_year=request.POST.get('vehicle_year', ''),

            # Step 6: Employment/Income
            employer_name=request.POST.get('employer_name', ''),
            employer_address1=request.POST.get('employer_address1', ''),
            employer_address2=request.POST.get('employer_address2', ''),
            employer_city=request.POST.get('employer_city', ''),
            employer_state=request.POST.get('employer_state', ''),
            employer_zip=request.POST.get('employer_zip', ''),
            employer_phone=request.POST.get('employer_phone', ''),
            monthly_salary=request.POST.get('monthly_salary') or 0,
            position=request.POST.get('position', ''),
            years_worked=request.POST.get('years_worked') or 0,
            supervisor_name=request.POST.get('supervisor_name', ''),

            # Step 7: Questions
            eviction_history=request.POST.get('eviction_history', 'no'),
            eviction_explain=request.POST.get('eviction_explain', ''),
            criminal_history=request.POST.get('criminal_history', 'no'),
            criminal_explain=request.POST.get('criminal_explain', ''),
            income_3x_rent=request.POST.get('income_3x_rent', 'yes'),
            income_explain=request.POST.get('income_explain', ''),
            employment_history=request.POST.get('employment_history', 'yes'),
            employment_explain=request.POST.get('employment_explain', ''),
            residency_history=request.POST.get('residency_history', 'yes'),
            residency_explain=request.POST.get('residency_explain', ''),

            # Step 9: Billing
            billing_first_name=request.POST.get('billing_first_name', ''),
            billing_last_name=request.POST.get('billing_last_name', ''),
            billing_address1=request.POST.get('billing_address1', ''),
            billing_address2=request.POST.get('billing_address2', ''),
            billing_city=request.POST.get('billing_city', ''),
            billing_state=request.POST.get('billing_state', ''),
            billing_zip=request.POST.get('billing_zip', ''),

            # Step 10: Terms & Authorization
            agree_terms=to_bool(request.POST.get('agree_terms')),
            authorized_name=request.POST.get('authorized_name', ''),
        )

        # --- Step 8: File Upload ---
        if 'photo_id' in request.FILES:
            photo = request.FILES['photo_id']
            timestamp = int(timezone.now().timestamp())
            filename = f"applying_{app.id}_{timestamp}_{photo.name}"
            file_path = os.path.join('photo_ids', filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb+') as f:
                for chunk in photo.chunks():
                    f.write(chunk)

            app.photo_id = file_path
            app.save()

        return redirect('add_application')

    return render(request, "frontend/applying.html", {'properties': properties})

def applyingList(request):
    applications = Applying.objects.all().order_by('-id')
    return render(request, "dashboard/applyingListing.html", {
        'applications': applications
    })

def application_detail(request, id):
    app = get_object_or_404(Applying, id=id)
    return render(request, "dashboard/viewListing.html", {"app": app})

def application_delete(request, id):
    app = get_object_or_404(Applying, id=id)
    app.delete()
    messages.success(request, f"Application for {app.first_name} {app.last_name} deleted successfully.")
    return redirect('applyingListDashboard')

def edit_applying(request, pk):
    applying = get_object_or_404(Applying, pk=pk)

    if request.method == 'POST':
        # Step 1
        applying.property_id = request.POST.get('property_id')
        move_in_date = request.POST.get('move_in_date')
        applying.move_in_date = move_in_date if move_in_date else None
        applying.applicant_type = request.POST.get('applicant_type')

        # Step 2
        applying.first_name = request.POST.get('first_name')
        applying.last_name = request.POST.get('last_name')
        applying.email = request.POST.get('email')
        applying.confirm_email = request.POST.get('confirm_email')
        applying.phone = request.POST.get('phone')
        applying.hear_about = request.POST.get('hear_about')

        # Step 3 – Previous residence
        applying.address1 = request.POST.get('address1')
        applying.address2 = request.POST.get('address2')
        applying.city = request.POST.get('city')
        applying.state = request.POST.get('state')
        applying.zipcode = request.POST.get('zipcode')
        applying.reside_from_month = request.POST.get('reside_from_month')
        applying.reside_from_year = request.POST.get('reside_from_year')
        applying.monthly_rent = request.POST.get('monthly_rent') or None
        applying.monthly_mortgage = request.POST.get('monthly_mortgage') or None
        applying.landlord_name = request.POST.get('landlord_name')
        applying.landlord_phone = request.POST.get('landlord_phone')
        applying.landlord_email = request.POST.get('landlord_email')
        applying.home_email = request.POST.get('home_email')
        applying.reason_for_leaving = request.POST.get('reason_for_leaving')

        # Step 4 – Boolean fields
        applying.other_adults = request.POST.get('other_adults') == 'on'
        applying.dependents_under_18 = request.POST.get('dependents_under_18') == 'on'
        applying.has_pets = request.POST.get('has_pets') == 'on'
        applying.has_vehicle = request.POST.get('has_vehicle') == 'on'
        applying.agree_terms = request.POST.get('agree_terms') == 'on'

        # Step 5 – Dates
        dob = request.POST.get('dob')
        applying.dob = dob if dob else None

        dependent_dob = request.POST.get('dependent_dob')
        applying.dependent_dob = dependent_dob if dependent_dob else None

        # Step 8 – File handling
        if 'photo_id' in request.FILES:
            applying.photo_id = request.FILES['photo_id']

        # Step 10 – Terms & authorization
        applying.authorized_name = request.POST.get('authorized_name')

        # Save updated record
        applying.save()
        return redirect('applyingListDashboard')

    return render(request, 'dashboard/applyingEdit.html', {'applying': applying})



