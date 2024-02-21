# Репликация и синхронизация проектов из сервиса Gitee

**Gitee Projects Replicator**, **GPReplicator** или **GPR** — это Python API, содержащее транспорт и методы для репликации и синхронизации проектов из русского сервиса Gitee.ru или китайского Gitee.com. Зеркалируемые проекты также могут содержать такую важную информацию как описание проекта, ишьюсы, майлстоуны, релизы и документацию.

Репликация и синхронизация работает через API.v5 сервиса Gitee.

Также GPReplicator может работать как консольный CLI-менеджер Gitee-проектов (он имеет богатый набор ключей и команд), что удобно для интеграции, при использовании в CI/CD-процессах, либо его можно использовать как обычный Python модуль через `python import gpreplicator`.

Если вы работаете с GPReplicator как с классом, каждый метод возвращает объект (обычно типа dict или list), содержащий все данные, доступные через API сервиса Gitee. Подробнее о методах класса GPReplicator можно прочитать здесь:
- ⚙ [Документация на методы классов GPReplicator (для Python-разработчиков)](https://3logicgroup.github.io/GiteeProjectsReplicator/docs/gpreplicator/GPReplicator.html)


## Быстрый старт и примеры

Вот простые примеры использования GPReplicator в консоли, после его установки. Для всех примеров вы должны использовать [Gitee OAuth токен](https://gitee.com/api/v5/oauth_doc):

- Получить рекурсивно и отобразить дерево файлов проекта (изменив gateway для API на китайский сервер):
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "ваш_токен" -go "владелец_группы_проектов" -gp "имя_репозитория" --gitee-recursive --files`
  
  Например:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "токен" -go tim55667757 -gp PriceGenerator --files`
  
- Получить и отобразить описание проекта:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "токен" -go "владелец" -gp "репозиторий" --description`
  
- Получить и отобразить список ишьюсов:
  
  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "токен" -go "владелец" -gp "репозиторий" --issues`
