from flask import Blueprint, flash, redirect, url_for, current_app, Response, render_template,request
from flask_login import login_required, current_user
from .models import Note, User, Share
from . import db
from .utils import get_validated_note
import re

share = Blueprint('share', __name__)

@share.route('/change_share_status/<note_id>')
@login_required
def change_share_status(note_id):
    note = get_validated_note(note_id)
    if isinstance(note, Response):
        return note

    if note.is_encrypted:
        flash('Note is encrypted and thus cannot be shared.')
        return redirect(url_for('main.profile'))

    if note.is_public:
        Note.query.filter_by(id=note.id).update(dict(is_public=False))
        db.session.commit()
        return redirect(url_for('main.profile'))
    else:
        return render_template('share_to.html', note_id=note_id)

@share.route('/change_share_status/<note_id>', methods=['POST'])
@login_required
def share_note(note_id):
    note = get_validated_note(note_id)
    if isinstance(note, Response):
        return note

    Share.query.filter_by(note_id=note.id).delete()

    emails = request.form['emails'].strip()
    for email in re.split(r',\s*', emails):
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('There is no user with email {}'.format(email))
            db.session.flush()
            return redirect(url_for('share.change_share_status', note_id=note_id))
        share = Share(note_id=note.id, viewer_id=user.id)
        db.session.add(share)

    db.session.commit()
    return redirect(url_for('main.note_show', note_id=note_id))