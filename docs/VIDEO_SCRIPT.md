# ReserveWeek · сценарий 1:55

Откройте `python3 -m demo.app` → http://127.0.0.1:8000, размер 1280×720, zoom 100%. Запись показывает два validation-примера; финальные test-результаты произносим отдельно. Графики и второй сервер не нужны. Суммы округлены для речи; на экране остаются точные значения из CSV.

| Время | Действие | Английская озвучка |
|---|---|---|
| 0:00–0:15 | Показать заголовок и дату. | Before buying stock, an online shopkeeper chooses a reserve for next week's recorded cancellations. ReserveWeek tests this decision using past sales and cancellations. This historical replay lets us inspect a covered week and a failure from one retailer using the same workflow. |
| 0:15–0:45 | Выбрать 4 апреля 2011, показать два резерва, нажать Reveal next week. | First, a validation example: April fourth. The model reserves about twenty-three thousand pounds. Recorded cancellations reach about thirteen thousand, leaving about ten thousand unused. The fixed comparison keeps the same historical amount each week. |
| 0:45–1:15 | Выбрать 18 января: факт скрывается. Нажать Reveal next week. | Now January eighteenth. Changing the date hides the result. We reserve twenty-four thousand pounds, but cancellations reach eighty-two thousand: a fifty-eight-thousand-pound shortfall. Recent history did not anticipate this spike. We do not know its cause. These are recorded invoice cancellations, not payment dates. |
| 1:15–1:45 | Оставить демо на экране; произнести итог test. | Our model blends a fixed reserve with a quantile regression. On 155 held-out decision dates, our fixed blend had £28.30 lower mean pinball loss than the constant reserve, but the paired 95% interval includes zero, so an advantage is not established. These seven-day targets overlap. |
| 1:45–1:55 | Показать ограничение внизу экрана или в write-up. | Next, we would test actual refund-payment records from a shop. The cost ratio is hypothetical. This project is a prototype and is not financial advice. |

До записи сверьте [write-up](../submission/SUMMARY.md) и [итоговый отчёт](../artifacts/final_results.md), затем прочитайте вслух с таймером; оставьте 5 секунд запаса до 2:00. Видео необязательно: сначала сдайте обязательные код и write-up. Загрузите запись как YouTube unlisted или Drive с просмотром по ссылке и проверьте доступ без входа.
