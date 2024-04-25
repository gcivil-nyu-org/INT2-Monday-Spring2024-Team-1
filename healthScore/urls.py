from django.urls import path
from django.contrib.auth import views as auth_views

from . import homepage_and_auth
from . import profile_view
from . import patient_view_records
from . import patient_submit_health_record
from . import healthcare_data
from . import community_data
from . import external_health_request_access
from . import admin_view_user_healthrecords
from . import doctor_data
from . import healthscore_admin_view


urlpatterns = [
    # Homepage and user auth
    path("homepage", homepage_and_auth.homepage, name="homepage"),
    path("registration/", homepage_and_auth.registration, name="registration"),
    path("login/", homepage_and_auth.login_view, name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset-done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Profile information
    path("editUserInfo", profile_view.edit_user_info, name="edit_user_info"),
    path("userInfo", profile_view.view_user_info, name="user_info"),
    # view records
    path(
        "viewRequests",
        patient_view_records.view_health_history_requests,
        name="view_requests",
    ),
    path(
        "viewHealthHistory",
        patient_view_records.view_health_history,
        name="view_health_history",
    ),
    path("viewReports", patient_view_records.view_report, name="view_reports"),
    path("getRecord/<str:rec_id>/", patient_view_records.get_record, name="get_record"),
    # Submitting health request apis
    path(
        "getDoctors/<str:hos_id>/",
        patient_submit_health_record.get_doctors,
        name="get_doctors",
    ),
    path(
        "getEdit/<str:rec_id>/", patient_submit_health_record.get_edit, name="get_edit"
    ),
    path(
        "edit-record/",
        patient_submit_health_record.edit_health_record_view,
        name="edit_record",
    ),
    path(
        "new-record/",
        patient_submit_health_record.add_health_record_view,
        name="new_health_record",
    ),
    path(
        "request-sent/",
        patient_submit_health_record.record_sent_view,
        name="new_health_record_sent",
    ),
    # Get healthcare related data
    path(
        "healthcareFacility/",
        healthcare_data.hospital_staff_directory,
        name="hospital_staff_directory",
    ),
    path(
        "getFacilityDoctors/",
        healthcare_data.get_facility_doctors,
        name="get_facility_doctors",
    ),
    path(
        "getFacilityAdmins/",
        healthcare_data.get_facility_admins,
        name="get_facility_admins",
    ),
    path(
        "addHealthcareStaff",
        healthcare_data.add_healthcare_staff,
        name="add_healthcare_staff",
    ),
    path(
        "deleteHealthcareStaff",
        healthcare_data.deactivate_healthcare_staff,
        name="deactivate_healthcare_staff",
    ),
    path(
        "activateHealthcareStaff",
        healthcare_data.activate_healthcare_staff,
        name="activate_healthcare_staff",
    ),
    path(
        "viewHealthHistoryDoc",
        patient_view_records.view_health_history_doc,
        name="view_health_history_doc",
    ),
    # community apis
    path("community/", community_data.community_home, name="community"),
    path("community/all-posts/", community_data.view_all_posts, name="all_posts"),
    path("community/my-posts/", community_data.view_my_posts, name="my_posts"),
    path("create-post", community_data.create_post, name="create_post"),
    path("edit-post/<int:post_id>/", community_data.edit_post, name="edit_post"),
    path("delete-post/<int:post_id>/", community_data.delete_post, name="delete_post"),
    path("view-post/<int:post_id>/", community_data.view_post, name="view_post"),
    path(
        "create-comments/<int:post_id>/comment/",
        community_data.create_comments,
        name="create_comments",
    ),
    path(
        "delete-comment/<int:comment_id>/",
        community_data.delete_comment,
        name="delete_comment",
    ),
    # External health request related apis
    path(
        "requestHealthHistory",
        external_health_request_access.request_health_history,
        name="request_health_history",
    ),
    path(
        "viewHealthHistoryAccessRequests",
        external_health_request_access.view_health_history_access_requests,
        name="view_health_history_access_requests",
    ),
    path(
        "update_request_status",
        external_health_request_access.update_request_status,
        name="update_request_status",
    ),
    path(
        "send-approval-emails",
        external_health_request_access.send_approval_emails,
        name="send_approval_emails",
    ),
    path(
        "send-reject-emails",
        external_health_request_access.send_rejection_emails,
        name="send_reject_emails",
    ),
    # health admin's view user records
    path(
        "recordDecision/",
        admin_view_user_healthrecords.view_healthworkers_user_record,
        name="view_healthworkers_user_record",
    ),
    path(
        "admin_view_records/",
        admin_view_user_healthrecords.admin_view_health_history_requests,
        name="admin_view_records",
    ),
    path(
        "adminGetEdit/<str:rec_id>/",
        admin_view_user_healthrecords.get_admin_edit,
        name="adminGetEdit",
    ),
    # Doctor related apis
    path("get_patients", doctor_data.get_patients, name="get_patients"),
    path(
        "get_doctor_details/<str:doctor_id>/",
        doctor_data.get_doctor_details,
        name="get_doctor_details",
    ),
    path(
        "get_patient_details/<str:patient_id>/",
        doctor_data.get_patient_details,
        name="get_patient_details",
    ),
    # healthScore admin apis
    path("hospitals/", healthscore_admin_view.list_hospitals, name="list_hospitals"),
    path(
        "hospitals/update_status/<int:hospital_id>/",
        healthscore_admin_view.update_hospital_status,
        name="update_hospital_status",
    ),
    path("userDashboard", homepage_and_auth.user_dashboard, name="user_dashboard"),
]
