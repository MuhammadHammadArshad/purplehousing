from django.db import models
from PIL import Image
import os
from django.core.files.base import ContentFile
from io import BytesIO
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)  # store hashed password
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)  # hash password
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.username

class Blog(models.Model):
    image = models.ImageField(upload_to="blogs/")
    title = models.CharField(max_length=200)
    description = models.TextField()
    keywords = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img_path = self.image.path
        img = Image.open(img_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=80)
        buffer.seek(0)
        new_filename = os.path.splitext(self.image.name)[0] + ".webp"
        self.image.save(new_filename, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'blogs'  # Table name in MySQL


# Booking the schedule
class Booking(models.Model):
    property_name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='Pending')
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    class Meta:
        db_table = 'booking'  # table name in DB

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.property_name}"




class Property(models.Model):
    prop_title = models.CharField(max_length=255)
    prop_des = models.TextField(blank=True, null=True)

    category = models.CharField(max_length=255, blank=True, null=True)
    purpose = models.CharField(max_length=255, blank=True, null=True)  # Status select

    prop_price = models.CharField(max_length=50)
    prop_beds = models.IntegerField(null=True, blank=True)
    prop_baths = models.IntegerField(null=True, blank=True)
    prop_size = models.CharField(max_length=50)
    prop_year_built = models.CharField(max_length=10, blank=True, null=True)

    # Store features as JSON array
    prop_features = models.JSONField(default=list, blank=True)

    property_map_address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    administrative_area_level_1 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    lat = models.CharField(max_length=100, blank=True)
    lng = models.CharField(max_length=100, blank=True)

    prop_google_street_view = models.CharField(max_length=10, default="hide")
    gallery_images = models.JSONField(default=list, blank=True)
    featured_image = models.IntegerField(
        default=0,
        help_text="Index of featured image in gallery_images"
    )
    attachments = models.JSONField(default=list, blank=True)
    video_file = models.CharField(max_length=255, blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    login_required = models.BooleanField(default=False)
    disclaimer = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, default="approved")

    created_at = models.DateTimeField(default=timezone.now)   # instead of auto_now_add
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = "Property"

    def __str__(self):
        return self.prop_title

# Choice tuples
STATE_CHOICES = [
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('TX', 'Texas'),
    # Add more as needed
]

MONTH_CHOICES = [(str(i), str(i)) for i in range(1, 13)]
DAY_CHOICES = [(str(i), str(i)) for i in range(1, 32)]
YEAR_CHOICES = [(str(y), str(y)) for y in range(1980, 2031)]  # adjust range

YES_NO_CHOICES = [('yes', 'Yes'), ('no', 'No')]

class Applying(models.Model):
    # Step 1
    property_id = models.CharField(max_length=10)
    move_in_date = models.DateField()
    APPLICANT_TYPE_CHOICES = [
        ('tenant', 'Tenant'),
        ('cosigner', 'Co-signer/Guarantor')
    ]
    applicant_type = models.CharField(max_length=10, choices=APPLICANT_TYPE_CHOICES)

    # Step 2
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    confirm_email = models.EmailField()
    phone = models.CharField(max_length=20)
    hear_about = models.CharField(max_length=50)

    # Step 3: Previous residence
    address1 = models.CharField(max_length=200, blank=True, null=True)
    address2 = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)
    zipcode = models.CharField(max_length=10, blank=True, null=True)
    reside_from_month = models.CharField(max_length=2, choices=MONTH_CHOICES, blank=True, null=True)
    reside_from_year = models.CharField(max_length=4, blank=True, null=True)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    monthly_mortgage = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    landlord_name = models.CharField(max_length=100, blank=True, null=True)
    landlord_phone = models.CharField(max_length=20, blank=True, null=True)
    landlord_email = models.EmailField(blank=True, null=True)
    home_email = models.EmailField(blank=True, null=True)
    reason_for_leaving = models.TextField(blank=True, null=True)

    # Step 4: Housemates
    other_adults = models.BooleanField(default=False)
    adult_count = models.PositiveSmallIntegerField(blank=True, null=True)
    adult_names = models.JSONField(blank=True, null=True)  # list of names
    adult_emails = models.JSONField(blank=True, null=True)
    adult_phones = models.JSONField(blank=True, null=True)

    dependents_under_18 = models.BooleanField(default=False)
    dependent_first_name = models.CharField(max_length=50, blank=True, null=True)
    dependent_last_name = models.CharField(max_length=50, blank=True, null=True)
    dependent_relation = models.CharField(max_length=50, blank=True, null=True)
    dependent_dob = models.DateField(blank=True, null=True)

    has_pets = models.BooleanField(default=False)
    pet_count = models.PositiveSmallIntegerField(blank=True, null=True)
    pet_details = models.JSONField(blank=True, null=True)  # list of dicts: {name, breed, weight, age}

    # Step 5: Personal info & vehicles
    dob = models.DateField(blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    license_state = models.CharField(max_length=20, blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    personal_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_relation = models.CharField(max_length=50, blank=True, null=True)
    ssn = models.CharField(max_length=100)

    has_vehicle = models.BooleanField(default=False)
    vehicle_make = models.CharField(max_length=50, blank=True, null=True)
    vehicle_color = models.CharField(max_length=20, blank=True, null=True)
    vehicle_license = models.CharField(max_length=20, blank=True, null=True)
    vehicle_modal = models.CharField(max_length=50, blank=True, null=True)
    vehicle_year = models.CharField(max_length=4, blank=True, null=True)

    # Step 6: Employment/Income
    employer_name = models.CharField(max_length=100, blank=True, null=True)
    employer_address1 = models.CharField(max_length=200, blank=True, null=True)
    employer_address2 = models.CharField(max_length=200, blank=True, null=True)
    employer_city = models.CharField(max_length=50, blank=True, null=True)
    employer_state = models.CharField(max_length=2, choices=STATE_CHOICES, blank=True, null=True)
    employer_zip = models.CharField(max_length=10, blank=True, null=True)
    employer_phone = models.CharField(max_length=20, blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    years_worked = models.PositiveSmallIntegerField(blank=True, null=True)
    supervisor_name = models.CharField(max_length=100, blank=True, null=True)

    # Step 7: Questions
    eviction_history = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='no')
    eviction_explain = models.TextField(blank=True, null=True)
    criminal_history = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='no')
    criminal_explain = models.TextField(blank=True, null=True)
    income_3x_rent = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='yes')
    income_explain = models.TextField(blank=True, null=True)
    employment_history = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='yes')
    employment_explain = models.TextField(blank=True, null=True)
    residency_history = models.CharField(max_length=3, choices=YES_NO_CHOICES, default='yes')
    residency_explain = models.TextField(blank=True, null=True)

    # Step 8: Documents
    photo_id = models.FileField(upload_to='photo_ids/')

    # Step 9: Billing
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_address1 = models.CharField(max_length=200)
    billing_address2 = models.CharField(max_length=200, blank=True, null=True)
    billing_city = models.CharField(max_length=50)
    billing_state = models.CharField(max_length=2, choices=STATE_CHOICES)
    billing_zip = models.CharField(max_length=10)

    # Step 10: Terms & Authorization
    agree_terms = models.BooleanField(default=False)
    authorized_name = models.CharField(max_length=100)

    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.property_id}"
