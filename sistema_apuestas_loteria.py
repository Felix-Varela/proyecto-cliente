import datetime
import webbrowser
from tkinter import *
from tkinter import ttk, messagebox

class AplicacionLoteria:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Apuestas de Lotería")
        self.root.geometry("1000x750")  # Aumenté un poco el tamaño para acomodar las nuevas funciones
        
        # Variables
        self.loterias = {
            "LA PRIMERA": {
                "apuesta_normal": (50, 15000),
                "horarios": ["10:00 AM", "6:00 PM"],
                "tiene_extra": False
            },
            "LA NICA": {
                "apuesta_normal": (50, 15000),
                "apuesta_extra": (0, 5000),
                "nombre_extra": "MULTI X",
                "horarios": ["11:00 AM", "3:00 PM", "6:00 PM", "9:00 PM"],
                "tiene_extra": True
            },
            "HONDURAS": {
                "apuesta_normal": (50, 15000),
                "horarios": ["11:00 AM", "3:00 PM", "9:00 PM"],
                "tiene_extra": False
            },
            "TICA": {
                "apuesta_normal": (50, 15000),
                "apuesta_extra": (0, 5000),
                "nombre_extra": "REVENTADO",
                "horarios": ["1:00 PM", "4:30 PM", "7:30 PM"],
                "tiene_extra": True
            }
        }
        
        self.ticket_actual = {
            "loteria": "",
            "horario": "",
            "hora_sorteo": None,
            "numeros": {},
            "apuesta_extra": 0
        }
        
        self.total_apuesta = 0
        self.hora_actual = datetime.datetime.now()
        self.tiempo_restante = StringVar(value="Tiempo restante: --:--")
        self.botones_eliminar = {}
        self.ultimo_monto_normal = 50
        self.ultimo_monto_extra = 0
        
        # Interfaz
        self.crear_interfaz()
        self.actualizar_hora()
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Frame de selección
        seleccion_frame = LabelFrame(main_frame, text="Selección de Lotería")
        seleccion_frame.pack(fill=X, pady=5)
        
        # Lotería
        Label(seleccion_frame, text="Lotería:").grid(row=0, column=0, padx=5, pady=5)
        self.loteria_var = StringVar()
        self.loteria_cb = ttk.Combobox(seleccion_frame, textvariable=self.loteria_var, 
                                     values=list(self.loterias.keys()))
        self.loteria_cb.grid(row=0, column=1, padx=5, pady=5)
        self.loteria_cb.bind("<<ComboboxSelected>>", lambda e: self.configurar_loteria())
        
        # Horario
        Label(seleccion_frame, text="Horario:").grid(row=0, column=2, padx=5, pady=5)
        self.horario_var = StringVar()
        self.horario_cb = ttk.Combobox(seleccion_frame, textvariable=self.horario_var)
        self.horario_cb.grid(row=0, column=3, padx=5, pady=5)
        
        # Tiempo restante
        Label(seleccion_frame, textvariable=self.tiempo_restante, 
              font=('Arial', 10, 'bold')).grid(row=0, column=4, padx=10, pady=5)
        
        # Frame de números individuales
        numeros_frame = LabelFrame(main_frame, text="Agregar Números Individuales")
        numeros_frame.pack(fill=X, pady=5)
        
        # Número
        Label(numeros_frame, text="Número (00-99):").grid(row=0, column=0, padx=5, pady=5)
        self.numero_var = StringVar()
        self.numero_entry = Entry(numeros_frame, textvariable=self.numero_var, width=5)
        self.numero_entry.grid(row=0, column=1, padx=5, pady=5)
        self.numero_entry.bind("<KeyRelease>", self.validar_numero)
        
        # Spinbox para número (solo flechas)
        self.numero_spin = Spinbox(numeros_frame, from_=0, to=99, width=3, 
                                 command=self.actualizar_numero_spin, format="%02.0f",
                                 state="readonly")
        self.numero_spin.grid(row=0, column=2, padx=5, pady=5)
        
        # Monto normal
        Label(numeros_frame, text="Monto Normal:").grid(row=0, column=3, padx=5, pady=5)
        self.monto_var = IntVar(value=self.ultimo_monto_normal)
        self.monto_entry = Entry(numeros_frame, textvariable=self.monto_var, width=10)
        self.monto_entry.grid(row=0, column=4, padx=5, pady=5)
        
        # Spinbox para monto normal (solo flechas)
        self.monto_spin = Spinbox(numeros_frame, from_=50, to=15000, increment=50, 
                                command=self.actualizar_monto_spin, width=8,
                                state="readonly")
        self.monto_spin.grid(row=0, column=5, padx=5, pady=5)
        
        # Frame para apuesta extra
        self.extra_frame = Frame(numeros_frame)
        self.extra_frame.grid(row=0, column=6, padx=5, pady=5)
        
        # Botón para agregar número
        Button(numeros_frame, text="Agregar", command=self.agregar_numero).grid(row=0, column=7, padx=5, pady=5)
        
        # Frame para series y terminaciones
        series_frame = LabelFrame(main_frame, text="Agregar por Series o Terminaciones")
        series_frame.pack(fill=X, pady=5)
        
        # Series (números que comienzan con)
        Label(series_frame, text="Serie (0-9):").grid(row=0, column=0, padx=5, pady=5)
        self.serie_var = StringVar()
        self.serie_cb = ttk.Combobox(series_frame, textvariable=self.serie_var, 
                                    values=[str(i) for i in range(10)], width=3)
        self.serie_cb.grid(row=0, column=1, padx=5, pady=5)
        
        # Terminaciones (números que terminan con)
        Label(series_frame, text="Terminación (0-9):").grid(row=0, column=2, padx=5, pady=5)
        self.terminacion_var = StringVar()
        self.terminacion_cb = ttk.Combobox(series_frame, textvariable=self.terminacion_var, 
                                          values=[str(i) for i in range(10)], width=3)
        self.terminacion_cb.grid(row=0, column=3, padx=5, pady=5)
        
        # Monto para series/terminaciones
        Label(series_frame, text="Monto por número:").grid(row=0, column=4, padx=5, pady=5)
        self.monto_serie_var = IntVar(value=self.ultimo_monto_normal)
        Entry(series_frame, textvariable=self.monto_serie_var, width=10).grid(row=0, column=5, padx=5, pady=5)
        
        # Botones para agregar series/terminaciones
        Button(series_frame, text="Agregar Serie", command=self.agregar_serie, 
              bg='#e6f3ff').grid(row=0, column=6, padx=5, pady=5)
        Button(series_frame, text="Agregar Terminación", command=self.agregar_terminacion,
              bg='#ffe6e6').grid(row=0, column=7, padx=5, pady=5)
        
        # Frame de ticket
        self.ticket_frame = LabelFrame(main_frame, text="Ticket Actual")
        self.ticket_frame.pack(fill=BOTH, expand=True, pady=5)
        
        # Crear un frame contenedor para el Treeview y la barra de desplazamiento
        tree_container = Frame(self.ticket_frame)
        tree_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(tree_container)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Treeview para mostrar los números
        self.columns = ('Numero', 'Monto Normal', 'Extra', 'Total')
        self.ticket_tree = ttk.Treeview(tree_container, columns=self.columns, show='headings',
                                      yscrollcommand=scrollbar.set)
        self.ticket_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.ticket_tree.yview)
        
        self.ticket_tree.heading('Numero', text='Número')
        self.ticket_tree.heading('Monto Normal', text='Monto Normal (₡)')
        self.ticket_tree.heading('Extra', text='Extra (₡)')
        self.ticket_tree.heading('Total', text='Total (₡)')
        
        self.ticket_tree.column('Numero', width=100, anchor='center')
        self.ticket_tree.column('Monto Normal', width=150, anchor='center')
        self.ticket_tree.column('Extra', width=150, anchor='center')
        self.ticket_tree.column('Total', width=150, anchor='center')
        
        # Frame para botones de eliminar (fuera del Treeview)
        self.botones_frame = Frame(self.ticket_frame)
        self.botones_frame.pack(fill=X, padx=5, pady=5)
        
        # Total
        self.total_label = Label(self.ticket_frame, text="Total: ₡0", font=('Arial', 10, 'bold'))
        self.total_label.pack(side=RIGHT, padx=10, pady=5)
        
        # Botones principales
        botones_frame = Frame(main_frame)
        botones_frame.pack(fill=X, pady=5)
        
        Button(botones_frame, text="Limpiar Ticket", command=self.limpiar_ticket).pack(side=LEFT, padx=5)
        Button(botones_frame, text="Enviar por WhatsApp", command=self.enviar_whatsapp).pack(side=RIGHT, padx=5)
    
    def agregar_serie(self):
        """Agrega todos los números que comienzan con el dígito seleccionado (0-9)"""
        serie = self.serie_var.get()
        monto = self.monto_serie_var.get()
        
        if not serie:
            messagebox.showerror("Error", "Seleccione un dígito para la serie (0-9)")
            return
        
        if not self.validar_loteria_horario():
            return
        
        # Validar monto
        min_normal, max_normal = self.loterias[self.ticket_actual["loteria"]]["apuesta_normal"]
        if monto < min_normal or monto > max_normal:
            messagebox.showerror("Error", f"Monto inválido. Debe estar entre ₡{min_normal} y ₡{max_normal}")
            return
        
        # Generar todos los números de la serie (0-9)
        numeros_serie = [f"{serie}{i}" for i in range(10)]
        
        # Preguntar confirmación
        if not messagebox.askyesno("Confirmar", f"¿Agregar serie {serie}X (10 números) con monto ₡{monto} cada uno?\nTotal: ₡{monto*10}"):
            return
        
        # Agregar todos los números de la serie
        for numero in numeros_serie:
            if numero in self.ticket_actual["numeros"]:
                # Si el número ya existe, preguntar si reemplazar
                if not messagebox.askyesno("Número existente", f"El número {numero} ya existe. ¿Reemplazar con nuevo monto?"):
                    continue
                else:
                    # Restar el monto anterior del total
                    self.total_apuesta -= (self.ticket_actual["numeros"][numero]["normal"] + 
                                         self.ticket_actual["numeros"][numero].get("extra", 0))
            
            # Agregar el número con el monto especificado
            self.ticket_actual["numeros"][numero] = {
                "normal": monto,
                "extra": 0
            }
            self.total_apuesta += monto
        
        self.actualizar_ticket_tree()
        self.ultimo_monto_normal = monto
        self.monto_var.set(monto)
    
    def agregar_terminacion(self):
        """Agrega todos los números que terminan con el dígito seleccionado (0-9)"""
        terminacion = self.terminacion_var.get()
        monto = self.monto_serie_var.get()
        
        if not terminacion:
            messagebox.showerror("Error", "Seleccione un dígito para la terminación (0-9)")
            return
        
        if not self.validar_loteria_horario():
            return
        
        # Validar monto
        min_normal, max_normal = self.loterias[self.ticket_actual["loteria"]]["apuesta_normal"]
        if monto < min_normal or monto > max_normal:
            messagebox.showerror("Error", f"Monto inválido. Debe estar entre ₡{min_normal} y ₡{max_normal}")
            return
        
        # Generar todos los números con la terminación (00-99)
        numeros_terminacion = [f"{i}{terminacion}" for i in range(10)]
        
        # Preguntar confirmación
        if not messagebox.askyesno("Confirmar", f"¿Agregar terminación X{terminacion} (10 números) con monto ₡{monto} cada uno?\nTotal: ₡{monto*10}"):
            return
        
        # Agregar todos los números de la terminación
        for numero in numeros_terminacion:
            if numero in self.ticket_actual["numeros"]:
                # Si el número ya existe, preguntar si reemplazar
                if not messagebox.askyesno("Número existente", f"El número {numero} ya existe. ¿Reemplazar con nuevo monto?"):
                    continue
                else:
                    # Restar el monto anterior del total
                    self.total_apuesta -= (self.ticket_actual["numeros"][numero]["normal"] + 
                                         self.ticket_actual["numeros"][numero].get("extra", 0))
            
            # Agregar el número con el monto especificado
            self.ticket_actual["numeros"][numero] = {
                "normal": monto,
                "extra": 0
            }
            self.total_apuesta += monto
        
        self.actualizar_ticket_tree()
        self.ultimo_monto_normal = monto
        self.monto_var.set(monto)
    
    def validar_loteria_horario(self):
        """Valida que se haya seleccionado lotería y horario"""
        if not all([self.ticket_actual["loteria"], self.ticket_actual["horario"]]):
            messagebox.showerror("Error", "Por favor seleccione lotería y horario primero")
            return False
        return True
    
    def configurar_loteria(self):
        loteria = self.loteria_var.get()
        if loteria in self.loterias:
            # Configurar horarios
            self.actualizar_sorteos_disponibles()
            self.horario_cb['values'] = self.loterias[loteria]["horarios_disponibles"]
            
            # Seleccionar el horario más próximo
            ahora = datetime.datetime.now()
            horario_proximo = None
            hora_sorteo_proximo = None
            menor_diferencia = None
            
            for horario in self.loterias[loteria]["horarios_disponibles"]:
                hora_str, ampm = horario.split()
                hora, minuto = map(int, hora_str.split(':'))
                
                if ampm == "PM" and hora != 12:
                    hora += 12
                elif ampm == "AM" and hora == 12:
                    hora = 0
                
                hora_sorteo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                diferencia = (hora_sorteo - ahora).total_seconds()
                
                if diferencia > 0 and (menor_diferencia is None or diferencia < menor_diferencia):
                    menor_diferencia = diferencia
                    horario_proximo = horario
                    hora_sorteo_proximo = hora_sorteo
            
            if horario_proximo:
                self.horario_var.set(horario_proximo)
                self.ticket_actual["hora_sorteo"] = hora_sorteo_proximo
                self.actualizar_tiempo_restante()
            
            # Configurar apuesta extra
            if self.loterias[loteria]["tiene_extra"]:
                self.extra_frame.grid()
                for widget in self.extra_frame.winfo_children():
                    widget.destroy()
                
                nombre_extra = self.loterias[loteria]["nombre_extra"]
                Label(self.extra_frame, text=f"{nombre_extra}:").pack(side=LEFT)
                
                self.extra_var = IntVar(value=self.ultimo_monto_extra)
                Entry(self.extra_frame, textvariable=self.extra_var, width=10).pack(side=LEFT, padx=5)
                
                Spinbox(self.extra_frame, from_=0, to=5000, increment=50, 
                       command=self.actualizar_extra_spin, width=8,
                       state="readonly").pack(side=LEFT)
                
                # Actualizar nombre de columna Extra
                self.ticket_tree.heading('Extra', text=f"{nombre_extra} (₡)")
            else:
                self.extra_frame.grid_remove()
                self.ticket_tree.heading('Extra', text='Extra (₡)')
            
            # Limpiar ticket anterior
            self.ticket_actual.update({
                "loteria": loteria,
                "horario": self.horario_var.get(),
                "numeros": {},
                "apuesta_extra": 0
            })
            self.total_apuesta = 0
            self.actualizar_ticket_tree()
            
            # Poner foco en número
            self.numero_entry.focus()
    
    def agregar_numero(self):
        if not all([self.ticket_actual["loteria"], self.ticket_actual["horario"]]):
            messagebox.showerror("Error", "Por favor seleccione lotería y horario primero")
            return
        
        try:
            numero = self.numero_var.get().zfill(2)
            monto_normal = self.monto_var.get()
            
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                monto_extra = self.extra_var.get()
            else:
                monto_extra = 0
            
            # Validar número
            if not numero.isdigit() or len(numero) != 2 or int(numero) < 0 or int(numero) > 99:
                messagebox.showerror("Error", "Número inválido. Debe ser entre 00 y 99")
                return
                
            # Validar montos
            min_normal, max_normal = self.loterias[self.ticket_actual["loteria"]]["apuesta_normal"]
            
            if monto_normal < min_normal or monto_normal > max_normal:
                messagebox.showerror("Error", f"Monto normal inválido. Debe estar entre ₡{min_normal} y ₡{max_normal}")
                return
                
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                min_extra, max_extra = self.loterias[self.ticket_actual["loteria"]]["apuesta_extra"]
                
                if monto_extra < min_extra or monto_extra > max_extra:
                    messagebox.showerror("Error", f"Monto {self.loterias[self.ticket_actual['loteria']]['nombre_extra']} inválido. Debe estar entre ₡{min_extra} y ₡{max_extra}")
                    return
                    
                if monto_extra > monto_normal:
                    messagebox.showerror("Error", f"El monto {self.loterias[self.ticket_actual['loteria']]['nombre_extra']} no puede ser mayor que el monto normal")
                    return
            
            # Agregar o actualizar número
            if numero in self.ticket_actual["numeros"]:
                if messagebox.askyesno("Confirmar", f"El número {numero} ya existe. ¿Desea reemplazarlo?"):
                    self.total_apuesta -= (self.ticket_actual["numeros"][numero]["normal"] + 
                                         self.ticket_actual["numeros"][numero].get("extra", 0))
                else:
                    return
            
            self.ticket_actual["numeros"][numero] = {
                "normal": monto_normal,
                "extra": monto_extra
            }
            
            # Guardar los montos usados para el próximo número
            self.ultimo_monto_normal = monto_normal
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                self.ultimo_monto_extra = monto_extra
            
            self.total_apuesta += monto_normal + monto_extra
            self.actualizar_ticket_tree()
            
            # Limpiar campos (excepto montos)
            self.numero_var.set('')
            # Mantener los montos del último número agregado
            self.monto_var.set(self.ultimo_monto_normal)
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                self.extra_var.set(self.ultimo_monto_extra)
            self.numero_entry.focus()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores válidos")
    
    def actualizar_ticket_tree(self):
        # Limpiar treeview y botones
        for item in self.ticket_tree.get_children():
            self.ticket_tree.delete(item)
        
        for widget in self.botones_frame.winfo_children():
            widget.destroy()
        
        # Configurar columnas según la lotería
        if self.ticket_actual["loteria"] in self.loterias:
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                nombre_extra = self.loterias[self.ticket_actual["loteria"]]["nombre_extra"]
                self.ticket_tree.heading('Extra', text=f"{nombre_extra} (₡)")
            else:
                self.ticket_tree.heading('Extra', text='Extra (₡)')
        
        # Agregar números al Treeview
        row_num = 0
        for numero, montos in self.ticket_actual["numeros"].items():
            valores = [numero, montos["normal"]]
            
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"]:
                valores.append(montos.get("extra", 0))
            else:
                valores.append('')
            
            total_numero = montos["normal"] + montos.get("extra", 0)
            valores.append(total_numero)
            
            self.ticket_tree.insert('', 'end', values=valores)
            
            # Crear botón de eliminar para este número
            btn_eliminar = Button(self.botones_frame, text=f"Eliminar {numero}", 
                                command=lambda n=numero: self.eliminar_numero(n),
                                width=12, bg='#ff9999', relief=FLAT)
            btn_eliminar.grid(row=0, column=row_num, padx=5, pady=5)
            row_num += 1
        
        # Actualizar total general
        self.total_label.config(text=f"Total: ₡{self.total_apuesta}")
        
        # Actualizar título del frame
        if self.ticket_actual["loteria"]:
            titulo = f"Ticket Actual - {self.ticket_actual['loteria']} {self.ticket_actual['horario']}"
            self.ticket_frame.config(text=titulo)
        else:
            self.ticket_frame.config(text="Ticket Actual")

    def eliminar_numero(self, numero):
        if numero in self.ticket_actual["numeros"]:
            self.total_apuesta -= (self.ticket_actual["numeros"][numero]["normal"] + 
                                 self.ticket_actual["numeros"][numero].get("extra", 0))
            del self.ticket_actual["numeros"][numero]
            self.actualizar_ticket_tree()

    def actualizar_tiempo_restante(self):
        if self.ticket_actual["hora_sorteo"]:
            ahora = datetime.datetime.now()
            tiempo_restante = self.ticket_actual["hora_sorteo"] - ahora - datetime.timedelta(minutes=10)
            
            if tiempo_restante.total_seconds() > 0:
                minutos, segundos = divmod(int(tiempo_restante.total_seconds()), 60)
                self.tiempo_restante.set(f"Tiempo restante: {minutos:02d}:{segundos:02d}")
            else:
                self.tiempo_restante.set("¡Tiempo agotado!")
                self.limpiar_ticket()
        else:
            self.tiempo_restante.set("Tiempo restante: --:--")
    
    def actualizar_hora(self):
        self.hora_actual = datetime.datetime.now()
        self.actualizar_sorteos_disponibles()
        self.actualizar_tiempo_restante()
        self.root.after(1000, self.actualizar_hora)
    
    def actualizar_sorteos_disponibles(self):
        ahora = datetime.datetime.now()
        for loteria, datos in self.loterias.items():
            nuevos_horarios = []
            for horario in datos["horarios"]:
                hora_str, ampm = horario.split()
                hora, minuto = map(int, hora_str.split(':'))
                if ampm == "PM" and hora != 12:
                    hora += 12
                elif ampm == "AM" and hora == 12:
                    hora = 0
                
                hora_sorteo = ahora.replace(hour=hora, minute=minuto, second=0, microsecond=0)
                limite_compra = hora_sorteo - datetime.timedelta(minutes=10)
                
                if ahora < limite_compra:
                    nuevos_horarios.append(horario)
            
            self.loterias[loteria]["horarios_disponibles"] = nuevos_horarios
        
        # Si hay un ticket en proceso y su horario ya no está disponible, limpiarlo
        if self.ticket_actual["horario"]:
            loteria_actual = self.ticket_actual["loteria"]
            if loteria_actual and self.ticket_actual["horario"] not in self.loterias[loteria_actual]["horarios_disponibles"]:
                self.limpiar_ticket()
                messagebox.showwarning("Tiempo agotado", f"Se ha cerrado la venta para el sorteo de {loteria_actual} a las {self.ticket_actual['horario']}")
    
    def limpiar_ticket(self):
        self.ticket_actual.update({
            "loteria": "",
            "horario": "",
            "hora_sorteo": None,
            "numeros": {},
            "apuesta_extra": 0
        })
        self.total_apuesta = 0
        self.actualizar_ticket_tree()
        self.loteria_var.set('')
        self.horario_var.set('')
        self.numero_var.set('')
        # Restablecer los montos a los valores por defecto al limpiar el ticket
        self.ultimo_monto_normal = 50
        self.ultimo_monto_extra = 0
        self.monto_var.set(50)
        if hasattr(self, 'extra_var'):
            self.extra_var.set(0)
        self.tiempo_restante.set("Tiempo restante: --:--")
    
    def enviar_whatsapp(self):
        if not self.ticket_actual["numeros"]:
            messagebox.showerror("Error", "No hay números en el ticket para enviar")
            return
        
        # Formatear mensaje
        mensaje = f"*Pedido de Apuestas*\n\n"
        mensaje += f"*Lotería:* {self.ticket_actual['loteria']}\n"
        mensaje += f"*Horario:* {self.ticket_actual['horario']}\n\n"
        mensaje += "*Números:*\n"
        
        for numero, montos in self.ticket_actual["numeros"].items():
            mensaje += f"{numero}: ₡{montos['normal']}"
            if self.loterias[self.ticket_actual["loteria"]]["tiene_extra"] and montos.get("extra", 0) > 0:
                mensaje += f" + {self.loterias[self.ticket_actual['loteria']]['nombre_extra']} ₡{montos['extra']}"
            mensaje += "\n"
        
        mensaje += f"\n*Total:* ₡{self.total_apuesta}\n"
        mensaje += f"\n*Hora de pedido:* {self.hora_actual.strftime('%I:%M %p')}"
        
        # Codificar mensaje para URL
        mensaje_url = f"https://wa.me/50671851264?text={mensaje.replace(' ', '%20').replace('\n', '%0A')}"
        
        # Abrir WhatsApp
        webbrowser.open(mensaje_url)
    
    # Métodos auxiliares para los spinboxes
    def actualizar_numero_spin(self):
        self.numero_var.set(self.numero_spin.get().zfill(2))
    
    def actualizar_monto_spin(self):
        self.monto_var.set(int(self.monto_spin.get()))
    
    def actualizar_extra_spin(self):
        if hasattr(self, 'extra_var'):
            self.extra_var.set(int(self.extra_frame.winfo_children()[2].get()))
    
    def validar_numero(self, event=None):
        numero = self.numero_var.get()
        if numero:
            # Solo permite hasta 2 dígitos numéricos
            if not numero.isdigit():
                self.numero_var.set('')
                return
            
            # Limitar a 2 caracteres
            if len(numero) > 2:
                self.numero_var.set(numero[:2])
            
            # Actualizar spinbox
            if numero.isdigit() and numero:
                self.numero_spin.config(state="normal")
                self.numero_spin.delete(0, END)
                self.numero_spin.insert(0, numero)
                self.numero_spin.config(state="readonly")

if __name__ == "__main__":
    root = Tk()
    app = AplicacionLoteria(root)
    root.mainloop()