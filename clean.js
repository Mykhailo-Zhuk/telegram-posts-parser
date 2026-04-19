#!/usr/bin/env node

/**
 * Clean script — видаляє завантажені файли та зображення
 * Запуск: node clean.js або npm run clean
 */

const fs = require("fs");
const path = require("path");

const filesToDelete = ["posts.json", "posts_reviewed.json"];
const dirToEmpty = "photos";

// Функція для отримання іконки за розширенням файлу
function getIconForExtension(ext) {
  const iconMap = {
    ".jpg": "📷",
    ".jpeg": "📷",
    ".png": "📷",
    ".gif": "📷",
    ".webp": "📷",
    ".mp4": "🎬",
    ".mov": "🎬",
    ".avi": "🎬",
    ".mkv": "🎬",
    ".webm": "🎬",
    ".pdf": "📄",
    ".doc": "📝",
    ".docx": "📝",
    ".txt": "📝",
    ".zip": "📦",
    ".rar": "📦",
    ".7z": "📦",
    ".session": "🔐",
  };
  return iconMap[ext.toLowerCase()] || "📎";
}

console.log("🧹 Очистка файлів...\n");

let totalDeleted = 0;

// Видалення JSON файлів
filesToDelete.forEach((file) => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    console.log(`  ✓ Видалено: ${file}`);
    totalDeleted++;
  } else {
    console.log(`  ⊘ Файл не знайдено: ${file}`);
  }
});

// Видалення медіа з папки
const photoDirPath = path.join(__dirname, dirToEmpty);
if (fs.existsSync(photoDirPath)) {
  const files = fs.readdirSync(photoDirPath);
  let mediaCount = 0;

  if (files.length > 0) {
    console.log(`\n  Медіа-файли:`);
    files.forEach((file) => {
      const filePath = path.join(photoDirPath, file);
      const stat = fs.statSync(filePath);

      if (stat.isFile()) {
        const ext = path.extname(file);
        const icon = getIconForExtension(ext);
        const sizeKB = (stat.size / 1024).toFixed(1);

        try {
          fs.unlinkSync(filePath);
          console.log(`    ${icon} ${file} (${sizeKB} KB)`);
          mediaCount++;
          totalDeleted++;
        } catch (e) {
          console.log(`    ⚠️  Помилка видалення ${file}: ${e.message}`);
        }
      }
    });

    if (mediaCount > 0) {
      console.log(`\n  ✓ Видалено ${mediaCount} медіа-файлів з папки ${dirToEmpty}/`);
    } else {
      console.log(`  ⊘ Папка ${dirToEmpty}/ пуста`);
    }
  } else {
    console.log(`\n  ⊘ Папка ${dirToEmpty}/ пуста`);
  }
} else {
  console.log(`  ⊘ Папка ${dirToEmpty}/ не існує`);
}

// Видалення session файлів Telethon
console.log(`\n  Session файли:`);
const sessionPatterns = ["session", "session.session"];
let sessionCount = 0;

sessionPatterns.forEach((pattern) => {
  const sessionPath = path.join(__dirname, pattern);
  if (fs.existsSync(sessionPath)) {
    try {
      fs.unlinkSync(sessionPath);
      console.log(`    🔐 ${pattern}`);
      sessionCount++;
      totalDeleted++;
    } catch (e) {
      console.log(`    ⚠️  Помилка видалення ${pattern}: ${e.message}`);
    }
  }
});

if (sessionCount === 0) {
  console.log(`    ⊘ Session файли не знайдені`);
}

// Підсумок
console.log(`\n${"═".repeat(50)}`);
console.log(`✨ Очистка завершена! Видалено ${totalDeleted} файлів`);
console.log(`${"═".repeat(50)}\n`);
