
def calcular_ic(temp, humedad):
    T, H = temp, humedad
    return round(
        -8.78469475556 + 1.61139411*T + 2.33854883889*H - 0.14611605*T*H -
        0.012308094*T**2 - 0.0164248277778*H**2 + 0.002211732*T**2*H +
        0.00072546*T*H**2 - 0.000003582*T**2*H**2, 1
    )


def nivel_desde_ic(ic):

    niveles = {
        "extremo": {
            "nivel":  "PELIGRO EXTREMO",
            "color":  "#ff1744",
            "clase":  "extremo",
            "icono":  "🔴",
            "emoji":  "🔥",
            "rango":  "IC ≥ 41°C",
            "recs": [
                {
                    "icono": "🚫",
                    "titulo": "Suspensión Total de Actividades",
                    "desc": "No realizar ninguna actividad física al aire libre. Permanecer en interiores con ventilación o aire acondicionado durante todo el día.",
                    "consecuencia": "La exposición puede provocar golpe de calor en menos de 20 minutos, con riesgo de daño cerebral permanente o muerte."
                },
                {
                    "icono": "💧",
                    "titulo": "Hidratación de Emergencia",
                    "desc": "Beber mínimo 250ml de agua cada 30 minutos. Evitar bebidas con cafeína o alcohol. Priorizar agua fría o con electrolitos.",
                    "consecuencia": "La deshidratación severa puede causar fallo renal, confusión mental y colapso cardiovascular."
                },
                {
                    "icono": "🏥",
                    "titulo": "Vigilancia Médica Activa",
                    "desc": "Monitorear constantemente a niños menores de 5 años, adultos mayores de 65 y personas con enfermedades crónicas. Tener a mano números de emergencia.",
                    "consecuencia": "Estos grupos pueden desarrollar golpe de calor sin síntomas previos visibles, con desenlace fatal en pocas horas."
                },
                {
                    "icono": "🌬️",
                    "titulo": "Refugio Climatizado Obligatorio",
                    "desc": "Cerrar ventanas y persianas antes de las 9am. Usar ventiladores y mantener espacios oscuros. Si no hay A/C, buscar centros comunitarios frescos.",
                    "consecuencia": "Una habitación sin ventilación puede alcanzar 10°C más que el exterior, agravando el riesgo de golpe de calor."
                },
                {
                    "icono": "🚑",
                    "titulo": "Señales de Alerta Médica",
                    "desc": "Ante piel caliente y seca, confusión, pérdida de consciencia, temperatura corporal > 40°C: llamar emergencias inmediatamente y aplicar paños fríos.",
                    "consecuencia": "El golpe de calor no tratado en los primeros 30 minutos tiene una tasa de mortalidad superior al 50%."
                },
            ]
        },
        "peligro": {
            "nivel":  "PELIGRO",
            "color":  "#ff6d00",
            "clase":  "peligro",
            "icono":  "🟠",
            "emoji":  "⚠️",
            "rango":  "IC 35–40°C",
            "recs": [
                {
                    "icono": "⏰",
                    "titulo": "Restricción de Horario Solar",
                    "desc": "Evitar exposición directa al sol entre las 10am y las 4pm. Si debe salir, hacerlo antes de las 9am o después de las 5pm.",
                    "consecuencia": "La exposición durante el pico solar puede generar agotamiento por calor con náuseas, debilidad extrema y desmayo."
                },
                {
                    "icono": "💧",
                    "titulo": "Hidratación Constante",
                    "desc": "Beber al menos 2 litros de agua durante el día aunque no sienta sed. Consumir frutas con alto contenido de agua como sandía o naranja.",
                    "consecuencia": "Sin hidratación adecuada el cuerpo pierde capacidad de regular la temperatura, aumentando el riesgo de golpe de calor."
                },
                {
                    "icono": "👕",
                    "titulo": "Vestimenta Adecuada",
                    "desc": "Usar ropa suelta, ligera y de colores claros (blanco, beige, celeste). Las fibras naturales como el algodón permiten mejor ventilación.",
                    "consecuencia": "La ropa oscura o ajustada puede elevar la temperatura corporal hasta 3°C adicionales bajo el sol."
                },
                {
                    "icono": "👶",
                    "titulo": "Protección de Grupos Vulnerables",
                    "desc": "Niños y adultos mayores deben permanecer en interiores. Nunca dejar niños o mascotas en vehículos estacionados, ni por un minuto.",
                    "consecuencia": "El interior de un auto puede superar los 60°C en minutos, causando muerte por golpe de calor en menos de una hora."
                },
                {
                    "icono": "🧴",
                    "titulo": "Protección Solar Total",
                    "desc": "Aplicar protector solar SPF 50+ cada 2 horas. Usar sombrero de ala ancha y lentes de sol con protección UV. Buscar sombra constantemente.",
                    "consecuencia": "La exposición solar acumulada aumenta el riesgo de golpe de calor y daño severo a largo plazo en piel y ojos."
                },
            ]
        },
        "precaucion": {
            "nivel":  "PRECAUCIÓN",
            "color":  "#ffab00",
            "clase":  "precaucion",
            "icono":  "🟡",
            "emoji":  "☀️",
            "rango":  "IC 32–34°C",
            "recs": [
                {
                    "icono": "🏃",
                    "titulo": "Moderar Actividad Física",
                    "desc": "Reducir ejercicio intenso al aire libre entre 11am y 3pm. Preferir actividades en espacios sombreados o interiores durante las horas pico.",
                    "consecuencia": "El ejercicio intenso con calor moderado puede provocar calambres, agotamiento y deshidratación acelerada."
                },
                {
                    "icono": "💧",
                    "titulo": "Aumentar Consumo de Agua",
                    "desc": "Beber agua antes, durante y después de cualquier actividad. No esperar a sentir sed, ya que es señal de que el cuerpo ya está deshidratado.",
                    "consecuencia": "La deshidratación leve reduce el rendimiento físico y cognitivo en un 20%, aumentando el riesgo de accidentes."
                },
                {
                    "icono": "🧴",
                    "titulo": "Protección Solar Básica",
                    "desc": "Aplicar protector solar SPF 30+ al salir. Usar ropa ligera y sombrero. Buscar sombra durante descansos al aire libre.",
                    "consecuencia": "Sin protección solar, la exposición continuada puede causar quemaduras, fatiga térmica y aumentar el riesgo de cáncer de piel."
                },
                {
                    "icono": "🌳",
                    "titulo": "Aprovechar Espacios Frescos",
                    "desc": "Descansar en zonas sombreadas o con brisa. Los parques con árboles pueden estar hasta 5°C más frescos que las calles sin vegetación.",
                    "consecuencia": "Permanecer en superficies de asfalto o concreto bajo el sol puede generar fatiga térmica en 30-45 minutos."
                },
                {
                    "icono": "👀",
                    "titulo": "Vigilar Síntomas Tempranos",
                    "desc": "Atención a dolor de cabeza, mareo leve o fatiga inusual. Son señales de que el cuerpo está bajo estrés térmico y necesita descanso y agua.",
                    "consecuencia": "Ignorar estos síntomas puede escalar a agotamiento por calor, que requiere atención médica urgente."
                },
            ]
        },
        "normal": {
            "nivel":  "NORMAL",
            "color":  "#00c853",
            "clase":  "normal",
            "icono":  "🟢",
            "emoji":  "✅",
            "rango":  "IC < 32°C",
            "recs": [
                {
                    "icono": "✅",
                    "titulo": "Condiciones Estables",
                    "desc": "El índice de calor es seguro para la mayoría de actividades al aire libre. Las condiciones climáticas de David están dentro de parámetros normales.",
                    "consecuencia": "Aunque el nivel es normal, el clima tropical de Chiriquí puede cambiar rápidamente. Mantener hidratación preventiva."
                },
                {
                    "icono": "💧",
                    "titulo": "Hidratación Preventiva",
                    "desc": "Beber al menos 1.5 litros de agua durante el día. Aun en condiciones normales, el clima húmedo de David acelera la pérdida de líquidos.",
                    "consecuencia": "La deshidratación crónica leve, aunque invisible, afecta la concentración, el estado de ánimo y la función renal a largo plazo."
                },
                {
                    "icono": "🌳",
                    "titulo": "Disfrute Responsable",
                    "desc": "Puede realizar actividades físicas y recreativas al aire libre. Aproveche las horas de menor radiación (antes de las 10am o después de las 4pm).",
                    "consecuencia": "Sin protección solar básica, incluso en días normales la exposición acumulada contribuye al envejecimiento prematuro de la piel."
                },
                {
                    "icono": "🧴",
                    "titulo": "Protección Solar Básica",
                    "desc": "Aunque el calor es tolerable, los rayos UV en Panamá son intensos durante todo el año. Usar protector solar SPF 30 al estar más de 20 minutos al exterior.",
                    "consecuencia": "Panamá recibe radiación UV alta o muy alta durante la mayor parte del año, independientemente de la temperatura percibida."
                },
            ]
        }
    }

    if ic >= 41:
        return niveles["extremo"]
    elif ic >= 35:
        return niveles["peligro"]
    elif ic >= 32:
        return niveles["precaucion"]
    else:
        return niveles["normal"]


def tiempo_seguro_exposicion(ic, actividad):
    """
    Calcula el tiempo máximo seguro de exposición al calor
    según el índice de calor y el tipo de actividad.
    Retorna minutos y un mensaje.
    """
    base = {
        "Descanso (sentado/parado)":       {41: 30,  35: 60,  32: 120, 0: 240},
        "Actividad ligera (caminar)":       {41: 15,  35: 30,  32: 60,  0: 120},
        "Actividad moderada (trabajo físico)": {41: 5, 35: 15, 32: 30,  0: 60},
        "Ejercicio intenso (deporte)":      {41: 0,   35: 5,   32: 15,  0: 30},
    }

    limites = base.get(actividad, base["Actividad ligera (caminar)"])

    if ic >= 41:
        minutos = limites[41]
    elif ic >= 35:
        minutos = limites[35]
    elif ic >= 32:
        minutos = limites[32]
    else:
        minutos = limites[0]

    if minutos == 0:
        return 0, "❌ No recomendado bajo ninguna circunstancia con este nivel de calor."
    elif minutos <= 15:
        return minutos, f"⚠️ Máximo {minutos} minutos. Descanso obligatorio de 30 min en interiores entre exposiciones."
    elif minutos <= 60:
        return minutos, f"🟡 Hasta {minutos} minutos con hidratación cada 15 min y a la sombra."
    else:
        horas = minutos // 60
        mins  = minutos % 60
        label = f"{horas}h {mins}min" if mins else f"{horas}h"
        return minutos, f"🟢 Hasta {label} con hidratación regular y protección solar."
