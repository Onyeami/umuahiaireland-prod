from django.urls import resolve


def dynamic_page_title(request):
    """
    Context processor to provide dynamic page titles based on current URL
    """
    try:
        # Get the current URL name
        url_name = resolve(request.path_info).url_name
        namespace = resolve(request.path_info).namespace

        # Define title mappings
        title_mappings = {
            # Public pages
            "index": "Home",
            "privacy_statement": "Privacy Statement",
            "send_email": "Contact Us",
            # Blog pages
            "blog:post_list": "Blog Posts",
            "blog:post_detail": "Blog Post",
            "blog:category_posts": "Category Posts",
            "blog:tag_posts": "Tag Posts",
            "blog:search": "Search Results",
            # User pages
            "user:dashboard": "Dashboard",
            "user:profile": "My Profile",
            "user:checkbooks": "Financial Checkbooks",
            "user:minuites": "Meeting Minutes",
            # Admin pages
            "admin:dashboard": "Dashboard",
            "admin:members": "Manage Members",
            "admin:minuites": "Manage Minutes",
            "admin:financial_checkbook": "Financial Checkbooks",
            "admin:create_minutes": "Create Minutes",
            "admin:edit_minuites": "Edit Minutes",
            "admin:create_checkbook": "Create Checkbook",
            "admin:edit_checkbook": "Edit Checkbook",
            "admin:settings": "Settings",
            "admin:blog_dashboard": "Blog Management",
            "admin:blog_posts": "Manage Blog Posts",
            "admin:blog_create_post": "Create Blog Post",
            "admin:blog_edit_post": "Edit Blog Post",
            "admin:blog_comments": "Manage Comments",
            "admin:blog_categories": "Manage Categories",
            "admin:blog_tags": "Manage Tags",
            "admin:create_user": "Create User",
            "admin:edit_user": "Edit User",
            # Authentication pages
            "accounts:login": "Login",
            "accounts:logout": "Logout",
            "accounts:register": "Register",
            "accounts:password_reset": "Password Reset",
        }

        # Get the full URL name with namespace
        full_url_name = f"{namespace}:{url_name}" if namespace else url_name

        # Get the page title
        page_title = title_mappings.get(
            full_url_name, url_name.replace("_", " ").title() if url_name else "Page"
        )

        # Determine page type and section for breadcrumbs
        page_type = ""
        page_section = ""
        if namespace == "admin":
            page_type = "Admin"
            page_section = "Administration"
        elif namespace == "user":
            page_type = "User"
            page_section = "User Portal"
        elif namespace == "blog":
            page_type = "Blog"
            page_section = "Blog"
        elif namespace == "accounts":
            page_type = "Account"
            page_section = "Authentication"
        else:
            page_section = "Public"

        return {
            "page_title": page_title,
            "page_type": page_type,
            "page_section": page_section,
            "current_url_name": url_name,
            "current_namespace": namespace or "",
            "is_admin_page": namespace == "admin",
            "is_user_page": namespace == "user",
            "is_blog_page": namespace == "blog",
            "is_auth_page": namespace == "accounts",
            "is_public_page": not namespace or namespace == "",
        }

    except Exception as e:
        # Fallback in case of errors
        return {
            "page_title": "Umuahia Community Ireland",
            "page_type": "",
            "page_section": "",
            "current_url_name": "",
            "current_namespace": "",
            "is_admin_page": False,
            "is_user_page": False,
            "is_blog_page": False,
            "is_auth_page": False,
            "is_public_page": True,
        }
