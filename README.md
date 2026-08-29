<div align="center">

<!-- ░░░ BORDE SUPERIOR — HEADER ANIMADO ░░░ -->
<img src="https://capsule-render.vercel.app/api?type=venom&color=0:0D0D0D,50:1a0533,100:0D0D0D&height=280&section=header&text=Plataforma%20de%20Trading%20Multiexchange&fontSize=45&fontColor=C084FC&animation=fadeIn&fontAlignY=45&stroke=7C3AED&strokeWidth=2&desc=▸%20para%20la%20Gestión%20de%20Criptomonedas,%20Tokens%20y%20Activos%20Digitales%◂&descAlignY=68&descSize=17&descColor=A78BFA" width="100%"/>

</div>

<!-- ░░░ LÍNEA DECORATIVA ░░░ -->
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

<br/>

<div align="center">

## ✦ &nbsp;Descripción&nbsp; ✦

<img src="https://media.giphy.com/media/qgQUggAC3Pfv687qPC/giphy.gif" width="380" alt="coding gif"/>

</div>

<br/>

&nbsp;&nbsp;&nbsp;&nbsp;El presente proyecto tiene como finalidad el diseño y desarrollo de una plataforma local para la gestión y simulación de operaciones de trading con activos digitales, orientada a integrar en un único sistema diferentes funcionalidades relacionadas con criptomonedas, tokens y NFT. Debido a su carácter académico, la solución será desarrollada y ejecutada exclusivamente en un entorno local, sin realizar despliegues en servidores públicos ni operaciones financieras reales.

La plataforma permitirá administrar activos digitales, consultar información del mercado y simular operaciones de compra y venta mediante diferentes tipos de órdenes, incluyendo órdenes de mercado (market), órdenes limitadas (limit) y órdenes de protección mediante stop-loss. Estas operaciones tendrán como objetivo demostrar el funcionamiento de los mecanismos de negociación y no implicarán el uso de dinero real.

Como parte del sistema se implementará un módulo de gestión de carteras multiactivo, que permitirá registrar y visualizar los activos disponibles, cantidades, movimientos, operaciones realizadas y valor estimado de la cartera. También se incorporarán funcionalidades básicas de seguimiento del rendimiento y exposición al riesgo, de acuerdo con el alcance definido para el proyecto.

La plataforma contará además con un módulo de gestión de riesgos, mediante el cual se podrán establecer límites y condiciones de protección para las operaciones simuladas. Se contemplará el uso de mecanismos como stop-loss, límites de operación y seguimiento de la exposición de los activos, con el propósito de demostrar cómo pueden aplicarse estrategias básicas de control del riesgo dentro de un sistema de trading.

Otro componente será la integración con múltiples exchanges mediante APIs, principalmente para obtener información de mercado, precios o datos de referencia. Debido al carácter académico del proyecto, estas integraciones estarán limitadas a las funcionalidades necesarias para demostrar el intercambio de información, evitando la implementación de procesos que requieran operar con fondos reales, custodiar credenciales financieras o mantener conexiones permanentes con servicios externos.

Desde el punto de vista tecnológico, se desarrollará una arquitectura modular y segura, que permita separar los principales componentes del sistema y facilitar su implementación, pruebas y mantenimiento durante el periodo académico. Se considerarán aspectos como autenticación de usuarios, almacenamiento de información, validación de operaciones, registro de actividades, manejo de errores y protección básica de los datos.

Finalmente, se desarrollará una interfaz gráfica centralizada desde la cual el usuario podrá consultar información del mercado, administrar sus carteras, crear órdenes simuladas, visualizar las operaciones realizadas y revisar el comportamiento de sus activos. La solución estará orientada principalmente a demostrar el funcionamiento de los conceptos y componentes de una plataforma de trading, priorizando la viabilidad, claridad y cumplimiento del alcance establecido para el proyecto de semestre..
<br/>

<!-- ░░░ LÍNEA DECORATIVA PUNTEADA ░░░ -->
<div align="center"><img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%"/></div>

<br/>

<!--
╔══════════════════════════════════════════════════════════════╗
║                       CÓDIGO FUENTE                         ║
╚══════════════════════════════════════════════════════════════╝
-->

<div align="center">

## ✦ &nbsp;Objetivo General y Especificos&nbsp; ✦

<img src="https://media.giphy.com/media/ZVik7pBtu9dNS/giphy.gif" width="320" alt="code animation"/>

</div>

<br/>

&nbsp;&nbsp;&nbsp;&nbsp;**Objetivo General:** <br/> Diseñar el prototipo de una plataforma académica para simular operaciones y gestión de carteras de activos digitales, integrando herramientas de mercado y control de riesgos sin riesgo financiero.

**Objetivos Específicos:** <br/>
**1.** Desarrollar el módulo central de operaciones que permita la simulación de compra y venta de criptomonedas, tokens y NFT, integrándolo con una interfaz gráfica que facilite la interacción del usuario.

**2.** Implementar un motor de ejecución de órdenes que soporte la gestión de transacciones simuladas mediante modalidades de mercado (market), límite (limit) y protección de pérdidas (stop-loss).

**3.** Estructurar un sistema de administración de carteras multiactivo que incorpore mecanismos de control de riesgos, tales como límites de operación, seguimiento de la exposición y protección del capital simulado.

**4.** Integrar APIs de múltiples exchanges para la obtención y sincronización de datos de mercado, alimentando la plataforma con información real de precios y activos para fines demostrativos y académicos.

<br/>

<!-- ░░░ SEPARADOR GIF ░░░ -->
<div align="center"><img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%"/></div>

<br/>

<div align="center">
  
## ✦ &nbsp;Patrones Creacionales&nbsp; ✦

<div align="left">
  
## &nbsp;Integracion Con Singleton&nbsp;

&nbsp;&nbsp;&nbsp;&nbsp;1. La elección del patrón Singleton para la integración de múltiples exchanges, responde a la necesidad arquitectónica de centralizar y proteger el acceso a los datos del mercado, evitando la inconsistencia de información y la saturación de los límites de peticiones (rate limits) impuestos por las APIs externas. Al tratarse de un entorno que debe alimentar simultáneamente diversos componentes asíncronos de la plataforma —como el motor de órdenes, la interfaz gráfica y el gestor de riesgos—, instanciar múltiples manejadores de conexión provocaría redundancia de red, desfases de milisegundos en los precios entre módulos y un consumo ineficiente de memoria. Por lo tanto, este patrón asegura que toda la arquitectura opere bajo una única "fuente de verdad" sincronizada, garantizando que un solo objeto gestione la recepción, el almacenamiento en caché y la distribución de los precios de los activos digitales de manera estable y unificada.

2. El patrón se implementa a nivel de infraestructura de clases en Python, interceptando la asignación de memoria mediante el método especial __new__ (en lugar del tradicional __init__). Su uso se detalla en tres mecanismos concretos:

* Contenedor estático (_instancia = None): Se declara un atributo a nivel de clase que actúa como un puntero estático. Su función es almacenar la única instancia viva del ExchangeConnectionManager en la memoria del programa.

* Control de instanciación (def __new__): Cuando un componente de tu plataforma solicita una conexión (ej. ExchangeConnectionManager()), el método verifica si _instancia está vacía. Solo en el primer llamado (cuando es None), invoca super().__new__(cls) para alojar el objeto en memoria y llama a _inicializar_conexion() para armar el caché de precios base.

* Retorno de referencia compartida: Si el objeto ya fue creado previamente, el método omite la creación y simplemente devuelve la referencia existente. Esto se evidencia en la línea api_interfaz is api_ordenes, la cual confirma de forma binaria que variables distintas en el código base están apuntando exactamente al mismo bloque de memoria.

3. Dentro del objetivo de integración con APIs, el Singleton se utiliza para resolver problemas críticos de sincronización y recursos en la simulación del trading:

* Garantizar una "Fuente de Verdad Única": Se utiliza para que la plataforma no tenga precios desfasados. Si ocurre una fluctuación en el mercado (mediante simular_actualizacion_mercado), el cambio impacta directamente el caché central. Así, el módulo de órdenes y el de la interfaz gráfica leen exactamente el mismo dato al mismo tiempo, previniendo fallos donde la interfaz apruebe una compra con un precio obsoleto.

* Simulación de multiplexación de conexiones: Se utiliza para preparar la base de código para el mundo real. En un entorno de producción con exchanges reales, mantener múltiples conexiones HTTP (o WebSockets) abiertas desde diferentes partes del código resultaría en bloqueos de IP por spam de solicitudes. El Singleton simula un embudo donde todas las partes del software le piden datos a un solo administrador local, y este administrador es el único autorizado para "hablar" con el exterior.

* Desacoplamiento de la lógica de mercado: Permite que cualquier componente acceda a los precios mediante una interfaz limpia (obtener_precio(par_activo)), ocultando toda la complejidad de qué exchanges están conectados, cómo funciona el caché, o cómo se gestionan los errores de red.

</div>
<br/>
<div align="left">

## &nbsp;CODIGO FUENTE&nbsp;

<img src="https://lh3.googleusercontent.com/d/1Rx4III5BgBIPJhePriACPgARKwUToEl7" width="100%"/>

</div>
<br/>

<!-- ░░░ SEPARADOR GIF ░░░ -->
<div align="center"><img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%"/></div>

<br/>

<div align="center">

## &nbsp;EVIDENCIA VIDEO&nbsp;

<a href="https://drive.google.com/file/d/15-t_hcsmN6Md2-Fpkiq4qMp9zkhHHYW7/view?usp=sharing" target="_blank">
  <img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" width="120" alt="Icono de Play"/>
  <br/>
</a>

</div>
</div>

<br/>

<!-- ░░░ SEPARADOR GIF ░░░ -->
<div align="center"><img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif" width="100%"/></div>

<br/>

<div align="center">

## ✦ &nbsp;Autor&nbsp; ✦

<img src="https://w7.pngwing.com/pngs/52/368/png-transparent-user-profile-computer-icons-avatar-avatar-heroes-monochrome-desktop-wallpaper.png" width="90" style="border-radius:50%; border: 3px solid #C084FC;"/>

**Harvey David Redondo Méndez**<br/>
**&**<br/>
**Arturo Hernandez Hernandez**

</div>

<br/>

<!-- ░░░ BORDE INFERIOR — FOOTER ANIMADO ░░░ -->
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%"/>

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:0D0D0D,50:1a0533,100:0D0D0D&height=130&section=footer&reversal=false&animation=fadeIn" width="100%"/>

</div>
