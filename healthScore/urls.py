from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("homepage", views.homepage, name="homepage"),
    path("registration/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
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
    path("editUserInfo", views.edit_user_info, name="edit_user_info"),
    path("userInfo", views.view_user_info, name="user_info"),
    path("viewRequests", views.view_health_history_requests, name="view_requests"),
    path("viewHealthHistory", views.view_health_history, name="view_health_history"),
    path("viewReports", views.view_report, name="view_reports"),
    # Submitting health request apis
    path("getDoctors/<str:hos_id>/", views.get_doctors, name="get_doctors"),
    path("getRecord/<str:rec_id>/", views.get_record, name="get_record"),
    path("getEdit/<str:rec_id>/", views.get_edit, name="get_edit"),
    path("edit-record/", views.edit_health_record_view, name="edit_record"),
    path("new-record/", views.add_health_record_view, name="new_health_record"),
    path("request-sent/", views.record_sent_view, name="new_health_record_sent"),
    path(
        "healthcareFacility/",
        views.hospital_staff_directory,
        name="hospital_staff_directory",
    ),
    path(
        "getFacilityDoctors/", views.get_facility_doctors, name="get_facility_doctors"
    ),
    path("getFacilityAdmins/", views.get_facility_admins, name="get_facility_admins"),
    path("addHealthcareStaff", views.add_healthcare_staff, name="add_healthcare_staff"),
    path(
        "deleteHealthcareStaff",
        views.deactivate_healthcare_staff,
        name="deactivate_healthcare_staff",
    ),
    path(
        "activateHealthcareStaff",
        views.activate_healthcare_staff,
        name="activate_healthcare_staff",
    ),
    # community
    path("community/", views.community_home, name="community"),
    path("community/all-posts/", views.view_all_posts, name="all_posts"),
    path("community/my-posts/", views.view_my_posts, name="my_posts"),
    path("create-post", views.create_post, name="create_post"),
    path("edit-post/<int:post_id>/", views.edit_post, name="edit_post"),
    path("delete-post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("view-post/<int:post_id>/", views.view_post, name="view_post"),
    path(
        "create-comments/<int:post_id>/comment/",
        views.create_comments,
        name="create_comments",
    ),
    path(
        "delete-comment/<int:comment_id>/",
        views.delete_comment,
        name="delete_comment",
    ),
    path(
        "requestHealthHistory",
        views.request_health_history,
        name="request_health_history",
    ),
    path(
        "viewHealthHistoryAccessRequests",
        views.view_health_history_access_requests,
        name="view_health_history_access_requests",
    ),
    path(
        "updateHealthHistoryAccessRequestStatus",
        views.update_health_history_access_request_status,
        name="update_health_history_access_request_status",
    ),
    path(
        "update_request_status",
        views.update_request_status,
        name="update_request_status",
    )
]
