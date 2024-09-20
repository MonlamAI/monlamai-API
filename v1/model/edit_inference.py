from v1.Config.Connection import prisma_connection,db


async def edit_inference(table: str, id: int, action: str, edit_data: str = None):

    # Dynamically access the correct table
    table_map = {
        'translation': db.translation,
        'speechtotexts': db.speechtotexts,
        'texttospeechs': db.texttospeech,
        'ocr': db.ocr
    }

    if table not in table_map:
        raise ValueError(f"Table '{table}' not found.")

    current_data = await table_map[table].find_unique(where={'id': id})
    if not current_data:
        raise ValueError(f"No record found for id '{id}' in table '{table}'.")
    
    update_data = {}

    # Handle the action
    if action == 'edit':
        if not edit_data:
            raise ValueError("No edit data provided for 'edit' action.")
        update_data['editOutput'] = edit_data

    elif action == 'like':
        # Increment the liked_count
        update_data['liked_count'] = {
            'increment': 1
        }
        if current_data.disliked_count > 0:
            update_data['disliked_count'] = {
                'decrement': 1
            }

    elif action == 'dislike':
        # Increment the disliked_count
        update_data['disliked_count'] = {
            'increment': 1
        }
        if current_data.liked_count > 0:
            update_data['liked_count'] = {
                'decrement': 1
            }

    else:
        raise ValueError(f"Unknown action '{action}'.")

    # Perform the update operation
    updated_data = await table_map[table].update(
        where={'id': id},
        data=update_data
    )

    return updated_data
