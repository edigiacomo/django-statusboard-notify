# Copyright (C) 2021 Emanuele Di Giacomo <emanuele@digiacomo.cc>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Recipient


class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'service_list')

    def service_list(self, o):
        return ", ".join(s.name for s in o.services.all())
    service_list.short_description = _('service list')


admin.site.register(Recipient, RecipientAdmin)
