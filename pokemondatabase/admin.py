from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(all_pokemon)
admin.site.register(pokemon_type)
admin.site.register(pokemon_ability)
admin.site.register(moveinfo)
admin.site.register(pokemon_moveset)
admin.site.register(user_movedata)
admin.site.register(pokemon_movedata)
admin.site.register(preevolution)
admin.site.register(unmatched_moves)
admin.site.register(pokemon_sprites)
admin.site.register(pokemon_tier) 
admin.site.register(pokemon_tier_template) 