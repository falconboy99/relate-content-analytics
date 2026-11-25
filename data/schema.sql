-- Portable PostgreSQL/SQLite-style relational schema. Optional; dashboard uses JSON.
CREATE TABLE posts (
 post_id TEXT PRIMARY KEY, content_id TEXT, title TEXT NOT NULL, topic TEXT NOT NULL,
 platform TEXT NOT NULL, published_at DATE NOT NULL, format TEXT NOT NULL, hook TEXT NOT NULL,
 variant TEXT CHECK (variant IN ('A','B','')), experiment_id TEXT,
 duration_seconds INTEGER NOT NULL CHECK(duration_seconds>=0),
 views INTEGER NOT NULL CHECK(views>=0), reach INTEGER NOT NULL CHECK(reach>=0),
 likes INTEGER NOT NULL CHECK(likes>=0), comments INTEGER NOT NULL CHECK(comments>=0),
 shares INTEGER NOT NULL CHECK(shares>=0), saves INTEGER NOT NULL CHECK(saves>=0),
 followers_gained INTEGER NOT NULL CHECK(followers_gained>=0),
 retention_rate REAL NOT NULL CHECK(retention_rate BETWEEN 0 AND 1),
 observation_hours INTEGER NOT NULL CHECK(observation_hours>0), source TEXT NOT NULL
);
CREATE TABLE comment_logs (
 comment_id TEXT PRIMARY KEY, post_id TEXT NOT NULL REFERENCES posts(post_id), text TEXT NOT NULL,
 created_at DATE NOT NULL, source TEXT NOT NULL, label TEXT CHECK(label IN ('Relatable','Neutral')),
 score REAL CHECK(score BETWEEN 0 AND 1), review BOOLEAN, reason TEXT
);
CREATE TABLE weekly_trends (
 topic TEXT NOT NULL, week DATE NOT NULL, "index" REAL NOT NULL CHECK("index" BETWEEN 0 AND 100),
 source TEXT NOT NULL, PRIMARY KEY(topic,week)
);
