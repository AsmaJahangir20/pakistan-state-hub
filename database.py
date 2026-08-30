import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "propertyhub.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _columns(cursor, table):
    return {
        row[1]
        for row in cursor.execute(
            f"PRAGMA table_info({table})"
        ).fetchall()
    }


def _add_column(cursor, table, name, definition):
    existing = _columns(cursor, table)

    if name not in existing:
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {name} {definition}"
        )


def init_database():
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                mobile TEXT NOT NULL UNIQUE,
                email TEXT UNIQUE,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL DEFAULT 'Buyer',
                province TEXT,
                city TEXT,
                address TEXT,
                profile_image TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                purpose TEXT NOT NULL,
                property_type TEXT NOT NULL,
                province TEXT NOT NULL,
                city TEXT NOT NULL,
                area_name TEXT,
                area_value REAL,
                area_unit TEXT,
                price REAL,
                price_period TEXT,
                bedrooms INTEGER DEFAULT 0,
                bathrooms INTEGER DEFAULT 0,
                furnished TEXT,
                condition TEXT,
                amenities TEXT,
                image_paths TEXT,
                contact_name TEXT,
                contact_mobile TEXT,
                property_address TEXT,
                latitude REAL,
                longitude REAL,
                property_registration_no TEXT,
                property_document_no TEXT,
                ownership_type TEXT,
                verification_status TEXT DEFAULT 'Pending',
                listing_status TEXT DEFAULT 'Active',
                ai_description TEXT,
                ai_match_score REAL,
                ai_price_insight TEXT,
                ai_risk_flags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS favourites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, property_id),
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                buyer_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT DEFAULT 'New',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (buyer_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                property_id INTEGER,
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (receiver_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                search_name TEXT NOT NULL,
                search_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS recently_viewed (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, property_id),
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reviewer_id INTEGER NOT NULL,
                property_id INTEGER NOT NULL,
                rating INTEGER NOT NULL
                    CHECK(rating BETWEEN 1 AND 5),
                review_text TEXT,
                status TEXT NOT NULL DEFAULT 'Visible',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(reviewer_id, property_id),
                FOREIGN KEY (reviewer_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reporter_id INTEGER NOT NULL,
                property_id INTEGER,
                reported_user_id INTEGER,
                report_type TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'Open',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reporter_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE SET NULL,
                FOREIGN KEY (reported_user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS admin_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                full_name TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS ai_conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS property_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                user_id INTEGER,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS property_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                document_type TEXT NOT NULL,
                document_number TEXT,
                document_path TEXT,
                verification_status TEXT DEFAULT 'Pending',
                admin_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS property_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                image_order INTEGER DEFAULT 0,
                is_cover INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS property_amenities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                amenity_name TEXT NOT NULL,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS property_status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                changed_by INTEGER,
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id)
                    REFERENCES properties(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (changed_by)
                    REFERENCES users(id)
                    ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                search_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE
            );
            """
        )

        # Safe upgrades for older databases.

        # USERS
        for name, definition in [
            ("address", "TEXT"),
            ("profile_image", "TEXT"),
            ("is_active", "INTEGER NOT NULL DEFAULT 1"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(cur, "users", name, definition)

        # PROPERTIES
        for name, definition in [
            ("image_paths", "TEXT"),
            ("contact_name", "TEXT"),
            ("contact_mobile", "TEXT"),
            ("property_address", "TEXT"),
            ("latitude", "REAL"),
            ("longitude", "REAL"),
            ("property_registration_no", "TEXT"),
            ("property_document_no", "TEXT"),
            ("ownership_type", "TEXT"),
            ("verification_status", "TEXT DEFAULT 'Pending'"),
            ("listing_status", "TEXT DEFAULT 'Active'"),
            ("ai_description", "TEXT"),
            ("ai_match_score", "REAL"),
            ("ai_price_insight", "TEXT"),
            ("ai_risk_flags", "TEXT"),
            ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ]:
            _add_column(cur, "properties", name, definition)

        # ENQUIRIES
        _add_column(
            cur,
            "enquiries",
            "updated_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

        # REVIEWS
        _add_column(
            cur,
            "reviews",
            "updated_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

        # REPORTS
        _add_column(
            cur,
            "reports",
            "admin_notes",
            "TEXT"
        )

        _add_column(
            cur,
            "reports",
            "updated_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

        # ADMIN USERS
        _add_column(
            cur,
            "admin_users",
            "full_name",
            "TEXT"
        )

        _add_column(
            cur,
            "admin_users",
            "is_active",
            "INTEGER NOT NULL DEFAULT 1"
        )

        # PROPERTY DOCUMENTS
        _add_column(
            cur,
            "property_documents",
            "verification_status",
            "TEXT DEFAULT 'Pending'"
        )

        _add_column(
            cur,
            "property_documents",
            "admin_notes",
            "TEXT"
        )

        _add_column(
            cur,
            "property_documents",
            "updated_at",
            "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        )

        # PROPERTY IMAGES
        _add_column(
            cur,
            "property_images",
            "image_order",
            "INTEGER DEFAULT 0"
        )

        _add_column(
            cur,
            "property_images",
            "is_cover",
            "INTEGER DEFAULT 0"
        )

        # Create default admin account.
        cur.execute(
            """
            INSERT OR IGNORE INTO admin_users
            (username, password, full_name, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (
                "admin",
                "admin123",
                "System Administrator",
                1
            )
        )

        # Create indexes.
        cur.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_users_mobile
            ON users(mobile);

            CREATE INDEX IF NOT EXISTS idx_users_email
            ON users(email);

            CREATE INDEX IF NOT EXISTS idx_users_city
            ON users(city);

            CREATE INDEX IF NOT EXISTS idx_users_province
            ON users(province);

            CREATE INDEX IF NOT EXISTS idx_properties_user
            ON properties(user_id);

            CREATE INDEX IF NOT EXISTS idx_properties_city
            ON properties(city);

            CREATE INDEX IF NOT EXISTS idx_properties_province
            ON properties(province);

            CREATE INDEX IF NOT EXISTS idx_properties_type
            ON properties(property_type);

            CREATE INDEX IF NOT EXISTS idx_properties_purpose
            ON properties(purpose);

            CREATE INDEX IF NOT EXISTS idx_properties_price
            ON properties(price);

            CREATE INDEX IF NOT EXISTS idx_properties_status
            ON properties(listing_status);

            CREATE INDEX IF NOT EXISTS idx_properties_verification
            ON properties(verification_status);

            CREATE INDEX IF NOT EXISTS idx_favourites_user
            ON favourites(user_id);

            CREATE INDEX IF NOT EXISTS idx_favourites_property
            ON favourites(property_id);

            CREATE INDEX IF NOT EXISTS idx_messages_sender
            ON messages(sender_id);

            CREATE INDEX IF NOT EXISTS idx_messages_receiver
            ON messages(receiver_id);

            CREATE INDEX IF NOT EXISTS idx_notifications_user
            ON notifications(user_id);

            CREATE INDEX IF NOT EXISTS idx_reviews_property
            ON reviews(property_id);

            CREATE INDEX IF NOT EXISTS idx_reports_property
            ON reports(property_id);

            CREATE INDEX IF NOT EXISTS idx_property_images_property
            ON property_images(property_id);

            CREATE INDEX IF NOT EXISTS idx_property_documents_property
            ON property_documents(property_id);

            CREATE INDEX IF NOT EXISTS idx_property_views_property
            ON property_views(property_id);

            CREATE INDEX IF NOT EXISTS idx_recently_viewed_user
            ON recently_viewed(user_id);

            CREATE INDEX IF NOT EXISTS idx_search_history_user
            ON search_history(user_id);
            """
        )

        conn.commit()

    finally:
        conn.close()


def add_demo_user():
    conn = get_connection()

    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO users
            (
                full_name,
                mobile,
                email,
                password,
                user_type,
                province,
                city,
                address,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Demo User",
                "03000000000",
                "demo@propertyhub.pk",
                "demo123",
                "Both",
                "Punjab",
                "Lahore",
                "Lahore, Punjab, Pakistan",
                1
            )
        )

        conn.commit()

    finally:
        conn.close()


def database_status():
    conn = get_connection()

    try:
        tables = conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        ).fetchall()

        return [row["name"] for row in tables]

    finally:
        conn.close()


def main():
    init_database()
    add_demo_user()

    print("==============================================")
    print("Pakistan Estate Hub Database")
    print("==============================================")
    print(f"Database location: {DB_PATH}")
    print("Database initialized successfully.")
    print("Default Admin Username: admin")
    print("Default Admin Password: admin123")
    print("==============================================")


if __name__ == "__main__":
    main()