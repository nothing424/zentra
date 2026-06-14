#!/usr/bin/env python3
"""
ZENTRA - Telegram Admin Bot
Sistem manajemen pengumuman via Telegram
Requires: pip install python-telegram-bot firebase-admin python-dotenv
"""

import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OWNER_ID = int(os.getenv('TELEGRAM_OWNER_ID', '0'))

# Firebase Admin
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json'))
firebase_admin.initialize_app(cred)
db = firestore.client()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

DIVIDER = '━' * 20

def is_owner(update: Update) -> bool:
    return update.effective_user.id == OWNER_ID

def format_date(dt=None):
    if dt is None:
        dt = datetime.now()
    return dt.strftime('%Y-%m-%d %H:%M WIB')

async def get_next_id() -> int:
    counter_ref = db.collection('_counters').document('announcements')
    counter = counter_ref.get()
    if counter.exists:
        current = counter.to_dict().get('value', 0)
    else:
        current = 0
    new_id = current + 1
    counter_ref.set({'value': new_id})
    return new_id

# ── COMMANDS ──────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        await update.message.reply_text('Akses ditolak.')
        return
    await update.message.reply_text(
        f'{DIVIDER}\n'
        f'ZENTRA ADMIN BOT\n'
        f'{DIVIDER}\n\n'
        f'Perintah yang tersedia:\n\n'
        f'/buatinfo [judul] | [isi]\n'
        f'/listinfo\n'
        f'/detailinfo [id]\n'
        f'/editinfo [id] | [judul] | [isi]\n'
        f'/hapusinfo [id]\n'
        f'/aktifinfo [id]\n'
        f'/nonaktifinfo [id]\n'
        f'/pininfo [id]\n\n'
        f'{DIVIDER}'
    )

async def cmd_buatinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    text = ' '.join(context.args)
    if '|' not in text:
        await update.message.reply_text('Format: /buatinfo [judul] | [isi]')
        return
    parts = text.split('|', 1)
    title = parts[0].strip()
    content = parts[1].strip()
    if not title or not content:
        await update.message.reply_text('Judul dan isi tidak boleh kosong.')
        return
    try:
        new_id = await get_next_id()
        now = datetime.now()
        doc = {
            'id': new_id,
            'title': title,
            'content': content,
            'type': 'Information',
            'priority': 'Normal',
            'active': True,
            'pinned': False,
            'views': 0,
            'createdAt': now.isoformat(),
            'updatedAt': now.isoformat(),
            'createdBy': 'Telegram Bot'
        }
        db.collection('announcements').document(str(new_id)).set(doc)
        await update.message.reply_text(
            f'{DIVIDER}\n'
            f'INFORMASI DIBUAT\n\n'
            f'ID: #{new_id}\n\n'
            f'Judul:\n{title}\n\n'
            f'Isi:\n{content}\n\n'
            f'Status:\nAktif\n\n'
            f'Prioritas:\nNormal\n\n'
            f'Dibuat:\n{format_date(now)}\n'
            f'{DIVIDER}'
        )
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_listinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    try:
        docs = db.collection('announcements').where('active', '==', True).order_by('id').get()
        items = [doc.to_dict() for doc in docs]
        if not items:
            await update.message.reply_text('Tidak ada informasi aktif.')
            return
        lines = '\n'.join([f"#{i['id']} {i['title']}" for i in items])
        await update.message.reply_text(
            f'{DIVIDER}\n'
            f'INFORMASI AKTIF\n\n'
            f'{lines}\n\n'
            f'Total: {len(items)}\n'
            f'{DIVIDER}'
        )
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_detailinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text('Format: /detailinfo [id]')
        return
    try:
        doc_id = context.args[0].replace('#', '')
        doc = db.collection('announcements').document(doc_id).get()
        if not doc.exists:
            await update.message.reply_text(f'Informasi #{doc_id} tidak ditemukan.')
            return
        d = doc.to_dict()
        await update.message.reply_text(
            f'{DIVIDER}\n'
            f'DETAIL INFORMASI\n\n'
            f'ID: #{d["id"]}\n'
            f'Judul: {d["title"]}\n'
            f'Isi: {d["content"]}\n'
            f'Tipe: {d["type"]}\n'
            f'Prioritas: {d["priority"]}\n'
            f'Status: {"Aktif" if d["active"] else "Nonaktif"}\n'
            f'Pin: {"Ya" if d["pinned"] else "Tidak"}\n'
            f'Views: {d["views"]}\n'
            f'Dibuat: {d["createdAt"][:16]}\n'
            f'Oleh: {d["createdBy"]}\n'
            f'{DIVIDER}'
        )
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_editinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    text = ' '.join(context.args)
    parts = text.split('|')
    if len(parts) < 3:
        await update.message.reply_text('Format: /editinfo [id] | [judul baru] | [isi baru]')
        return
    try:
        doc_id = parts[0].strip().replace('#', '')
        new_title = parts[1].strip()
        new_content = parts[2].strip()
        db.collection('announcements').document(doc_id).update({
            'title': new_title,
            'content': new_content,
            'updatedAt': datetime.now().isoformat()
        })
        await update.message.reply_text(
            f'{DIVIDER}\n'
            f'INFORMASI DIPERBARUI\n\n'
            f'ID: #{doc_id}\n'
            f'Judul Baru: {new_title}\n'
            f'Isi Baru: {new_content}\n'
            f'{DIVIDER}'
        )
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_hapusinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text('Format: /hapusinfo [id]')
        return
    try:
        doc_id = context.args[0].replace('#', '')
        db.collection('announcements').document(doc_id).delete()
        await update.message.reply_text(
            f'{DIVIDER}\n'
            f'INFORMASI DIHAPUS\n\n'
            f'ID: #{doc_id}\n\n'
            f'Status:\nBerhasil Dihapus\n'
            f'{DIVIDER}'
        )
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_aktifinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text('Format: /aktifinfo [id]')
        return
    try:
        doc_id = context.args[0].replace('#', '')
        db.collection('announcements').document(doc_id).update({'active': True, 'updatedAt': datetime.now().isoformat()})
        await update.message.reply_text(f'Informasi #{doc_id} diaktifkan.')
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_nonaktifinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text('Format: /nonaktifinfo [id]')
        return
    try:
        doc_id = context.args[0].replace('#', '')
        db.collection('announcements').document(doc_id).update({'active': False, 'updatedAt': datetime.now().isoformat()})
        await update.message.reply_text(f'Informasi #{doc_id} dinonaktifkan.')
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

async def cmd_pininfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return
    if not context.args:
        await update.message.reply_text('Format: /pininfo [id]')
        return
    try:
        doc_id = context.args[0].replace('#', '')
        # Unpin all first
        docs = db.collection('announcements').where('pinned', '==', True).get()
        for doc in docs:
            doc.reference.update({'pinned': False})
        # Pin the selected
        db.collection('announcements').document(doc_id).update({'pinned': True, 'updatedAt': datetime.now().isoformat()})
        await update.message.reply_text(f'Informasi #{doc_id} disematkan.')
    except Exception as e:
        await update.message.reply_text(f'Error: {e}')

def main():
    if not BOT_TOKEN:
        print('ERROR: TELEGRAM_BOT_TOKEN tidak ditemukan di .env')
        return
    if OWNER_ID == 0:
        print('ERROR: TELEGRAM_OWNER_ID tidak ditemukan di .env')
        return

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('buatinfo', cmd_buatinfo))
    app.add_handler(CommandHandler('listinfo', cmd_listinfo))
    app.add_handler(CommandHandler('detailinfo', cmd_detailinfo))
    app.add_handler(CommandHandler('editinfo', cmd_editinfo))
    app.add_handler(CommandHandler('hapusinfo', cmd_hapusinfo))
    app.add_handler(CommandHandler('aktifinfo', cmd_aktifinfo))
    app.add_handler(CommandHandler('nonaktifinfo', cmd_nonaktifinfo))
    app.add_handler(CommandHandler('pininfo', cmd_pininfo))

    print('Zentra Telegram Bot berjalan...')
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
