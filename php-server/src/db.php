<?php
// SQLite data access layer. All data is local — the site works fully offline
// after skills have been synced (see bin/sync.php).

declare(strict_types=1);

const DB_PATH = __DIR__ . '/../../data/skills.db';
const SKILLS_DIR = __DIR__ . '/../../data/skills';

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        if (!file_exists(DB_PATH)) {
            throw new RuntimeException('数据库不存在，请先运行 php php-server/bin/sync.php 抓取技能');
        }
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }
    return $pdo;
}

function initSchema(PDO $pdo): void
{
    $pdo->exec(<<<'SQL'
        CREATE TABLE IF NOT EXISTS skills (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            handle        TEXT NOT NULL,
            slug          TEXT NOT NULL,
            name          TEXT DEFAULT '',
            description   TEXT DEFAULT '',
            description_zh TEXT DEFAULT '',
            category      TEXT DEFAULT '',
            category_name TEXT DEFAULT '',
            version       TEXT DEFAULT '',
            icon_url      TEXT DEFAULT '',
            source        TEXT DEFAULT '',
            source_url    TEXT DEFAULT '',
            downloads     INTEGER DEFAULT 0,
            stars         INTEGER DEFAULT 0,
            installs      INTEGER DEFAULT 0,
            keywords      TEXT DEFAULT '',   -- which sync keywords matched this skill
            synced_at     INTEGER DEFAULT 0,
            UNIQUE(handle, slug)
        );
        CREATE TABLE IF NOT EXISTS files (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            path     TEXT NOT NULL,
            sha256   TEXT DEFAULT '',
            size     INTEGER DEFAULT 0,
            UNIQUE(skill_id, path)
        );
        CREATE TABLE IF NOT EXISTS meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category);
        CREATE INDEX IF NOT EXISTS idx_skills_downloads ON skills(downloads DESC);
    SQL);
}

function skillDir(string $handle, string $slug): string
{
    $key = preg_replace('/[^\w@.-]/', '_', ($handle ?: '_') . '__' . $slug);
    return SKILLS_DIR . '/' . $key;
}

function isSafeRelPath(string $path): bool
{
    return $path !== '' && !str_starts_with($path, '/') && !in_array('..', explode('/', $path), true);
}

/**
 * Search skills in the local database.
 */
function searchSkills(array $q): array
{
    $page = max(1, (int)($q['page'] ?? 1));
    $pageSize = min(100, max(1, (int)($q['pageSize'] ?? 24)));
    $where = [];
    $args = [];

    if (!empty($q['keyword'])) {
        $kw = '%' . trim($q['keyword']) . '%';
        $where[] = '(name LIKE ? OR description LIKE ? OR description_zh LIKE ? OR slug LIKE ?)';
        array_push($args, $kw, $kw, $kw, $kw);
    }
    if (!empty($q['category'])) {
        $where[] = 'category = ?';
        $args[] = $q['category'];
    }
    $whereSql = $where ? 'WHERE ' . implode(' AND ', $where) : '';

    $sort = match ($q['sort'] ?? '') {
        'downloads' => 'downloads DESC',
        'stars' => 'stars DESC',
        'installs' => 'installs DESC',
        'newest' => 'synced_at DESC',
        default => '(downloads * 2 + stars * 10 + installs) DESC',
    };

    $stmt = db()->prepare("SELECT COUNT(*) FROM skills $whereSql");
    $stmt->execute($args);
    $total = (int)$stmt->fetchColumn();

    $stmt = db()->prepare("SELECT * FROM skills $whereSql ORDER BY $sort LIMIT ? OFFSET ?");
    $stmt->execute([...$args, $pageSize, ($page - 1) * $pageSize]);

    return [
        'skills' => $stmt->fetchAll(),
        'total' => $total,
        'page' => $page,
        'pageSize' => $pageSize,
    ];
}

function getSkill(string $handle, string $slug): ?array
{
    $stmt = db()->prepare('SELECT * FROM skills WHERE handle = ? AND slug = ?');
    $stmt->execute([$handle, $slug]);
    $skill = $stmt->fetch();
    if (!$skill) return null;

    $stmt = db()->prepare('SELECT path, sha256, size FROM files WHERE skill_id = ? ORDER BY path');
    $stmt->execute([$skill['id']]);
    $skill['files'] = $stmt->fetchAll();
    return $skill;
}

function getCategories(): array
{
    return db()->query(
        'SELECT category AS key, category_name AS name, COUNT(*) AS count
         FROM skills WHERE category != "" GROUP BY category ORDER BY count DESC'
    )->fetchAll();
}

function getStats(): array
{
    $db = db();
    $meta = [];
    foreach ($db->query('SELECT key, value FROM meta') as $row) {
        $meta[$row['key']] = $row['value'];
    }
    return [
        'skills' => (int)$db->query('SELECT COUNT(*) FROM skills')->fetchColumn(),
        'files' => (int)$db->query('SELECT COUNT(*) FROM files')->fetchColumn(),
        'categories' => (int)$db->query('SELECT COUNT(DISTINCT category) FROM skills')->fetchColumn(),
        'lastSync' => isset($meta['last_sync']) ? (int)$meta['last_sync'] : null,
        'keywords' => isset($meta['keywords']) ? json_decode($meta['keywords'], true) : [],
    ];
}
