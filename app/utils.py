ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def find_overlaps(users, current_user, Like):
    overlaps = []
    for user_to_check in users:
        if user_to_check.id != current_user.get_id():
            overlaps.append([0, user_to_check.id, user_to_check.username])

    for user_to_check in overlaps:
        user_id = user_to_check[1]
        user_likes = Like.query.filter_by(user_id=user_id).all()
        for like in user_likes:
            if Like.query.filter_by(user_id=current_user.get_id(), post_id=like.post_id).count() > 0:
                user_to_check[0] += 1
    overlaps.sort(reverse=True)
    return overlaps
