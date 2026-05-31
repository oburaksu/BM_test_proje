# =============================================
# Factory Boy Test Verisi Üreticileri
# =============================================
# Bu modül testlerde kullanmak üzere rastgele ve gerçekçi test verileri
# üretmek için Factory Boy ve Faker kütüphanelerini kullanır.
#
# Model Factory pattern: Test yazarken uzun uzun nesne oluşturmak yerine
# TaskFactory() diyerek kurallara uygun rastgele bir görev oluşturulmasını sağlar.

import factory
from faker import Faker
from src.models.task import Task, Tag

# Faker nesnesi, Türkçe veri üretecek şekilde ayarlandı
fake = Faker('tr_TR')


class TagFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Tag (Etiket) modeli için test verisi üretici."""

    class Meta:
        model = Tag
        # Session ataması test içinde yapılacak
        sqlalchemy_session_persistence = "commit"

    # Etiket ismi için faker'dan rastgele bir kelime al
    name = factory.LazyFunction(lambda: fake.word())


class TaskFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Task (Görev) modeli için test verisi üretici."""

    class Meta:
        model = Task
        sqlalchemy_session_persistence = "commit"

    # Görev başlığı: Faker ile rastgele bir cümle oluştur
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4))
    
    # Açıklama: Rastgele bir paragraf
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    
    # Tamamlanma durumu: Varsayılan False olsun
    is_completed = False

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        """Çoka-çok ilişkideki etiketleri atamak için post_generation kancası."""
        if not create:
            # Sadece nesne bellekte oluşturuluyorsa hiçbir şey yapma
            return

        if extracted:
            # Eğer test yazan kişi `TaskFactory(tags=[tag1, tag2])` derse onları ekle
            for tag in extracted:
                self.tags.append(tag)
