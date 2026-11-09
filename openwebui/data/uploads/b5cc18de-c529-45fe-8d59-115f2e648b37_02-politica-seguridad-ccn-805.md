# Política de seguridad según CCN-STIC 805

## 🎯 Qué aprenderás

- ✅ Definir el **concepto de política de seguridad de la información** y diferenciarla de otros documentos.
- ✅ Enumerar el **contenido mínimo que exige el ENS** (art. 12) y la **estructura y componentes** que propone la guía CCN-STIC 805.
- ✅ Explicar quién la aprueba, cómo se publica y cómo se mantiene viva mediante **revisión periódica**.
- ✅ Distinguir **política, normas, guías y procedimientos** de seguridad.
- ✅ Conocer los **criterios de categorización de sistemas según CCN** (ENS) y su relación con la proporcionalidad de los requisitos.

## 📖 ¿Qué es una política de seguridad?

El **Esquema Nacional de Seguridad** (Real Decreto 311/2022) define la **política de seguridad de la información** como *el conjunto de directrices que rigen la forma en que una organización gestiona y protege la información que trata y los servicios que presta*.

> **💡 Definición clave**
> La **política de seguridad de la información** es un documento **de alto nivel** que establece **qué** se quiere conseguir en materia de seguridad, sin entrar en detalles técnicos ni nombrar productos concretos.

La guía **CCN-STIC 805**, del Centro Criptológico Nacional (CCN), la describe como un documento que dice qué significa «seguridad de la información» en la organización. Por eso debe ser:

- **Accesible** para todos los miembros de la organización.
- **Sencilla, precisa y comprensible**.
- **Breve**: los detalles técnicos se dejan para otros documentos (normas, guías, procedimientos).

La guía ofrece pautas generales, válidas para entidades de distinta naturaleza y tamaño, y se espera que cada organización las **adapte a su entorno**. Su versión más reciente se ha actualizado al Real Decreto 311/2022 y al marco jurídico nacional y europeo, e incorpora novedades en responsabilidades, principios, aprobación y publicación, así como su relación con la protección de datos y la inteligencia artificial.

!!! warning "Importante"
    La política **no** nombra productos ni soluciones tecnológicas concretas. Debe expresar *qué* se quiere conseguir, de modo que el cambio de herramientas no obligue a reescribirla.

## 📋 Contenido mínimo según el ENS (art. 12)

El artículo 12 del ENS obliga a que el documento que aprueba la política incluya, **como mínimo**, estos seis elementos:

1. Los **objetivos o misión** de la organización.
2. El **marco regulatorio** en el que se desarrollan sus actividades.
3. Los **roles o funciones de seguridad**, con sus deberes y responsabilidades y el procedimiento para designarlos y renovarlos.
4. La **estructura y composición de los comités** de gestión y coordinación de la seguridad, con su ámbito de responsabilidad.
5. Las directrices para **estructurar la documentación** de seguridad, su gestión y su acceso.
6. Los **riesgos derivados del tratamiento de datos personales**.

> **💡 Idea clave**
> Estos seis puntos son el **núcleo obligatorio**. La política puede tener más contenido, pero nunca menos.

Además, la política se establece de acuerdo con los **principios básicos del ENS** y se desarrolla aplicando unos **requisitos mínimos** (organización del proceso de seguridad, análisis y gestión de riesgos, gestión de personal, profesionalidad, control de accesos, protección de instalaciones, adquisición de productos y servicios, mínimo privilegio, integridad y actualización del sistema, protección de la información, prevención ante sistemas interconectados, registro de actividad y detección de código dañino, incidentes, continuidad y mejora continua).

!!! tip "Proporcionalidad"
    Estos requisitos se exigen **en proporción a los riesgos** de cada sistema. Aquí es donde entran los **criterios de categorización de sistemas según CCN** (ENS): los sistemas se clasifican en categorías (básico, medio, alto) según su impacto, y a cada categoría se le aplican los requisitos correspondientes.

## 🏗️ Estructura y componentes que propone la guía CCN-STIC 805

La CCN-STIC 805 sugiere organizar la **política de seguridad** en estas secciones (estructura y componentes):

| Sección | Qué recoge |
|---|---|
| **Misión** | La razón de ser de la organización y los servicios que presta. |
| **Marco normativo** | Las obligaciones legales, sectoriales y contraídas con terceros, indicando las normas. |
| **Organización de la seguridad** | Comités, roles unipersonales (en especial el **Responsable de Seguridad**), funciones, coordinación y designación. |
| **Gestión de riesgos** | Metodología, criterios de aceptación, relación con el análisis de riesgos y categorización de sistemas. |
| **Protección de la información** | Clasificación, etiquetado, manipulación, almacenamiento, transmisión y destrucción. |
| **Servicios y comunicaciones** | Seguridad en redes, comunicaciones, servicios externos y en la nube. |
| **Gestión de personal** | Concienciación, formación, obligaciones, acceso y revocación. |
| **Planificación y continuidad** | Planes de continuidad, backup, pruebas y mejora continua. |
| **Cumplimiento y auditoría** | Auditorías internas/externas, indicadores, reporting y revisión por la dirección. |

```mermaid
flowchart TD
    POL[Política de Seguridad
    (alto nivel)] --> NOR[Normas de seguridad
    Obligatorias, concretas]
    POL --> GUI[Guías de seguridad
    Formativas, flexibles]
    POL --> PRO[Procedimientos de seguridad
    Paso a paso, repetitivos]
    NOR --> USO[Uso diario por el personal]
    GUI --> USO
    PRO --> USO
    USO --> REV[Revisión periódica
    Mejora continua]
    REV --> POL
```

### Jerarquía documental

Como la política es muy general (alto nivel), se complementa con documentos más concretos:

- **Normas de seguridad:** Uniformizan aspectos concretos del sistema, indican el uso correcto y las responsabilidades de los usuarios. Son **obligatorias**.
- **Guías de seguridad:** Tienen carácter formativo y ayudan a aplicar bien las medidas donde no hay procedimientos precisos.
- **Procedimientos de seguridad:** Describen **paso a paso** tareas concretas, útiles en tareas repetitivas.

> **💡 Diferencia clave**
> | Documento | Nivel | Obligatoriedad | Ejemplo |
> |---|---|---|---|
> | Política | Estratégico (qué) | Sí | "Se protegerá la confidencialidad de los datos" |
> | Norma | Táctico (cómo general) | Sí | "Todo dato sensible se cifrará en reposo y en tránsito" |
> | Guía | Operativo (recomendaciones) | No | "Buenas prácticas para cifrar bases de datos" |
> | Procedimiento | Operativo (pasos exactos) | Sí | "Pasos para configurar cifrado LUKS en disco" |

Distinguir con claridad entre la **política** (abstracta) y su **aplicación concreta** da flexibilidad y mantiene resultados uniformes aunque cambie la tecnología.

## 🏛️ Criterios de categorización de sistemas según CCN (ENS)

El ENS establece que los requisitos de seguridad se aplican **en proporción a los riesgos** de cada sistema. Para ello, los sistemas se **categorizan** según su **impacto** en tres dimensiones:

| Categoría | Impacto en la misión | Impacto en derechos/libertades | Ejemplo |
|---|---|---|---|
| **Básico** | Limitado | Limitado | Web informativa corporativa |
| **Medio** | Grave | Grave | Sistema de gestión de RRHH |
| **Alto** | Muy grave / Catastrófico | Muy grave / Catastrófico | Sistema de historia clínica, infraestructura crítica |

Esta **categorización** determina qué **requisitos mínimos** del anexo II del ENS son de aplicación obligatoria y con qué nivel de detalle. La guía CCN-STIC 805 detalla cómo realizar esta categorización y cómo adaptar la política a cada categoría.

## ✅ Aprobación, publicación y revisión

Cada administración pública debe contar con una política **formalmente aprobada por el órgano competente**; en la Administración General del Estado, cada ministerio aprueba la suya, y los municipios pueden compartir una política común elaborada por la entidad local comarcal o provincial. La guía recuerda que la política tiene **carácter imperativo** sobre toda la organización y que el proceso de elaboración y aprobación debe explicitarse en ella.

La política no es un documento que se archiva y se olvida:

- Se somete a **revisión regular** para adaptarla a nuevas circunstancias técnicas u organizativas y evitar que quede obsoleta.
- Se comprueba su **oportunidad, idoneidad, completitud y precisión**, y se aprueba de nuevo formalmente.
- Las revisiones suelen ser **continuistas**: mejoran expresiones ambiguas, ganan claridad y cubren situaciones imprevistas. No se cambia de política «alegremente», pero se adapta de forma continua a la realidad.

## 📝 Resumen

- La **política de seguridad** es un documento **breve y de alto nivel** que define cómo se gestiona y protege la información y los servicios (**concepto**).
- El ENS (art. 12) exige que recoja: **misión, marco regulatorio, roles, comités, estructura documental y riesgos de datos personales**.
- La guía **CCN-STIC 805** propone una **estructura y componentes** en 9 secciones (misión, marco normativo, organización, gestión de riesgos, protección de la información, servicios, personal, continuidad, cumplimiento).
- Los **requisitos mínimos** se aplican **en proporción a los riesgos** según la **categorización de sistemas** (básico, medio, alto).
- La aprueba formalmente el **órgano competente** y obliga a toda la organización.
- Se desarrolla mediante **normas, guías y procedimientos** (jerarquía documental).
- Se **revisa periódicamente** para que no quede obsoleta.

## 🔑 Conceptos clave

- **Política de seguridad de la información:** Directrices que rigen cómo una organización gestiona y protege su información y servicios.
- **CCN-STIC 805:** Guía del CCN con un modelo y pautas para elaborar la política conforme al ENS.
- **Comité de seguridad:** Órgano que gestiona y coordina la seguridad de la organización.
- **Responsable de Seguridad:** Rol unipersonal con funciones y responsabilidades definidas en la política.
- **Categorización de sistemas (ENS):** Clasificación en básico, medio o alto según el impacto potencial.
- **Norma:** Documento obligatorio que regula el uso correcto de un aspecto del sistema.
- **Procedimiento:** Instrucciones paso a paso para una tarea concreta.
- **Proporcionalidad:** Principio por el que los requisitos se adaptan al nivel de riesgo del sistema.

## 📚 Documentación oficial

- [Real Decreto 311/2022 – Esquema Nacional de Seguridad (BOE)](https://www.boe.es/eli/es/rd/2022/05/03/311/con): Texto consolidado; el artículo 12 recoge la política de seguridad.
- [CCN-STIC 805 – Política de Seguridad de la Información](https://www.ccn-cert.cni.es/es/800-guia-esquema-nacional-de-seguridad/508-ccn-stic-805-politica-de-seguridad-de-la-informacion/file.html): Guía oficial del CCN-CERT.
- [CCN – Actualización de guías CCN-STIC Serie 800](https://www.ccn.cni.es/ca/menu-actualitat-ccn-ca-es/1282-actualizacion-de-cinco-guias-ccn-stic-de-la-serie-800-conforme-al-real-decreto-311-2022-y-a-los-nuevos-retos-de-la-ciberseguridad): Comunicado de las nuevas versiones alineadas con el RD 311/2022.
- [ENS – Portal oficial](https://ens.ccn.cni.es/): Normativa y guías del Esquema Nacional de Seguridad.
