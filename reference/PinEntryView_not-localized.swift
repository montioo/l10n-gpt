//
//  PinEntryView.swift
//  edl21-control
//
//  Created by Marius Montebaur on 19.09.23.
//

import SwiftUI


let confirmationExplanationText = "Halten Sie Ihr iPhone so nah wie möglich vor den EDL21 Zähler, damit das Blitzlicht des iPhones die optische Schnittstelle im Zähler erreicht."
let bruteForceExplanationText = "Im Brute Force Modus probiert die App alle möglichen Kombinationen von der eingegebenen Pin bis 9999 durch. Dieses Verhalten kann in den Einstellungen wieder deaktiviert werden."


struct PinEntryView: View {
    
    @State private var selectedPin: String? = nil
    
    // This is always in sync with the digits displayed in the UI. If they change, the UI changes, if the UI changes, these nunbers change.
    @State private var displayedPin: Pin = Pin(d0: nil, d1: nil, d2: nil, d3: nil)
    
    @StateObject var pinDict: UserDefaultsModel<PinDict>
    @StateObject var bruteForceModeEnabled: UserDefaultsModel<Bool>
    @Binding var pinString: String
    
    @State private var showingStorePinDialog = false
    @State private var newPinName = ""
    
    @State private var showingInvalidPinWarning: Bool = false
    @State private var showingReadyConfirmation: Bool = false
    
    
    func setDisplayedPinFromSelectedPin() {
        if selectedPin == nil {
            return
        }
        
        if pinDict.value[selectedPin!] == nil {
            selectedPin = nil
            return
        }
        
        let newPin: [Int] = pinDict.value[selectedPin!]!
        displayedPin.d0 = newPin[0]
        displayedPin.d1 = newPin[1]
        displayedPin.d2 = newPin[2]
        displayedPin.d3 = newPin[3]
    }
    
    // used as a UI update
    func setDisplayedPinFromInt(pin: Int) {
        let pinArray = pinArrayFromPinInt(pinInt: pin)
        displayedPin.d0 = pinArray[0]
        displayedPin.d1 = pinArray[1]
        displayedPin.d2 = pinArray[2]
        displayedPin.d3 = pinArray[3]
        
        if pinString.count == 4 {
            pinString = formatPinString(pin: pin)
        }
    }
    
    func formatPinString(pin: Int) -> String {
        return String(format: "%04d", pin)
    }
    
    func startPinEntry() {
        guard let pinArray = pinArrayFromDisplayedPin(displayedPin: displayedPin) else { return }
        
        let pinInt = pinIntFromPinArray(pinArray: pinArray)
        pinString = formatPinString(pin: pinInt)
    }
    
    // Pin Entry is disabled (i.e. overlay is hidden) by setting pinString to ""
    // This is pretty ugly as this code is duplicated in the pin unlock in progress overlay
    func pinEntryDone() {
        pinString = ""
        abortCurrentJob()
    }
    
    var body: some View {
        NavigationView {
            Form {
                
                // Text("DEBUG: \(displayedPin.d0 ?? -1), \(displayedPin.d1 ?? -1), \(displayedPin.d2 ?? -1), \(displayedPin.d3 ?? -1)")
                if bruteForceModeEnabled.value {
                    Section(footer: Text(bruteForceExplanationText)) {
                        HStack {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .renderingMode(.template)
                                .foregroundColor(.red)
                            Text("Brute Force Modus aktiviert!")
                                .foregroundColor(.red)
                                .bold()
                        }
                    }
                }
                
                Section(header: Text("Eingabe der Pin")) {
                    PinView(pin: $displayedPin)
                        .padding(.top, 10)
                        .padding(.bottom, 10)
                        .onChange(of: displayedPin) { newValue in
                            // if displayed pin is not in the values of the dict, set the picker selection to nil
                            let pinArrays = Array(pinDict.value.values)
                            let pinInts: [Int] = pinArrays.map { pa in pinIntFromPinArray(pinArray: pa) }
                            guard let displayedArray = pinArrayFromDisplayedPin(displayedPin: displayedPin) else {
                                return
                            }
                            let displayedInt = pinIntFromPinArray(pinArray: displayedArray)
                            
                            if !pinInts.contains(displayedInt) {
                                selectedPin = nil
                            }
                        }
                        .alignmentGuide(.listRowSeparatorLeading) { d in
                            // https://www.hackingwithswift.com/quick-start/swiftui/how-to-adjust-list-row-separator-insets
                            -20
                        }
                    
                    Button(action: {
                        if !isDisplayedPinValid(displayedPin: displayedPin) {
                            showingInvalidPinWarning = true
                            return
                        }
                        showingReadyConfirmation = true
                    }, label: {
                        HStack() {
                            Spacer()
                            Image(systemName: "lock.open.fill")
                            Text("Entsperren")
                            Spacer()
                        }
                    })
                }
                
                Section(footer: Text("Gespeicherte Pins können in den Einstellungen verwaltet werden.")) {
                    
                    if self.pinDict.value.count > 0 {
                        Picker("Ausgewählte Pin", selection: $selectedPin) {
                            ForEach(pinDictSortedKeys(self.pinDict.value), id: \.self) { key in
                                Text("\(key)").tag(key as String?)
                            }
                            Divider()
                            Text("Nicht gespeichert").tag(nil as String?)
                        }
                        .onChange(of: selectedPin) { newValue in
                            // print("selected \(newValue ?? "")")
                            setDisplayedPinFromSelectedPin()
                        }
                        .onAppear(perform: {
                            // if displayed pin is invalid (i.e. contains nil), display the first stored pin
                            if !isDisplayedPinValid(displayedPin: displayedPin) {
                                selectedPin = pinDictSortedKeys(self.pinDict.value)[0]
                                setDisplayedPinFromSelectedPin()
                            }
                            
                        })
                        .alignmentGuide(.listRowSeparatorLeading) { _ in -20 }
                    }
                    
                    StorePinButton(pinDict: pinDict, showingStorePinDialog: $showingStorePinDialog, newPinName: $newPinName, displayedPin: $displayedPin, selectedPinInUi: $selectedPin, showingInvalidPinWarning: $showingInvalidPinWarning)
                }
                
            }
            .navigationBarTitle(Text("Zähler entsperren"))
            .onAppear {
                // If this is not done here, it can lead to problems when the stored pins where changed in the settings and the UI can go out of sync with the data.
                if selectedPin != nil {
                    let storedPins = pinDictSortedKeys(self.pinDict.value)
                    if !storedPins.contains(selectedPin!) {
                        selectedPin = storedPins.count > 0 ? storedPins[0] : nil
                    }
                }
                setDisplayedPinFromSelectedPin()
            }
            
            // --- Pin invalid alert ---
            
            .alert("Pin ungültig", isPresented: $showingInvalidPinWarning) {
                Button(role: .cancel, action: {
                    // canceling
                }, label: {
                    Text("Verstanden")
                })
            } message: {
                Text("Die angegebene Pin ist nicht gültig. Bitte geben Sie eine gülitge Pin ein.")
            }
            
            
            // --- Ready confirmation alert ---
            
            .alert("Bereit?", isPresented: $showingReadyConfirmation) {
                Button(role: .cancel, action: { showingReadyConfirmation = false }, label: {
                    Text("Abbrechen")
                })
                Button(action: {
                    showingReadyConfirmation = false
                    startPinEntry()
                    let pinArray = pinArrayFromDisplayedPin(displayedPin: displayedPin)!
                    let pinInt = pinIntFromPinArray(pinArray: pinArray)
                    _ = startBlinkingPin(pinInt: pinInt, uiUpdateCallback: setDisplayedPinFromInt, uiEndCallback: pinEntryDone)
                }, label: {
                    Text("Los geht's")
                })
            } message: {
                Text(confirmationExplanationText)
            }
            
            
            // --- Unlock in Progress alert is handled in containing view ---
            
        }
        /*
         .onTapGesture {
         resignFirstResponder()
         }
         */
        
    }
}

struct PinEntryView_Previews: PreviewProvider {
    static var previews: some View {
        PinEntryView(
            pinDict: UserDefaultsModel<PinDict>(userDefaultsKey: "dummy", defaultValue: ["Oben": [5, 6, 7, 8]]),
            bruteForceModeEnabled: UserDefaultsModel<Bool>(userDefaultsKey: "dbe", defaultValue: true),
            pinString: Binding(get: { return "1111" }, set: { v in })
            )
            
    }
}
