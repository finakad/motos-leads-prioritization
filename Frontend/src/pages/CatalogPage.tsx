import { Bike, Shield, Gauge, Check } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { formatCurrency } from '@/lib/utils'

export function CatalogPage() {
  const motorcycles = [
    {
      id: 'moto-01',
      brand: 'Yamaha',
      model: 'MT-03 ABS',
      displacement: '321 cc',
      category: 'Hyper Naked',
      price: 32500000,
      stock: 4,
      features: ['Frenos ABS doble canal', 'Motor bicilíndrico DOHC', 'Iluminación Full LED'],
    },
    {
      id: 'moto-02',
      brand: 'KTM',
      model: '390 Duke',
      displacement: '398 cc',
      category: 'Naked Sport',
      price: 31990000,
      stock: 2,
      features: ['Cornering ABS', 'Launch Control', 'Pantalla TFT 5"'],
    },
    {
      id: 'moto-03',
      brand: 'Bajaj',
      model: 'Pulsar NS 200 FI ABS',
      displacement: '199.5 cc',
      category: 'Sport Urbano',
      price: 13990000,
      stock: 9,
      features: ['Inyección electrónica', 'Refrigeración líquida', 'Suspensión invertida'],
    },
    {
      id: 'moto-04',
      brand: 'Kawasaki',
      model: 'Ninja 400 KRT Edition',
      displacement: '399 cc',
      category: 'Supersport',
      price: 38990000,
      stock: 1,
      features: ['Embrague asistido y antirebote', 'Chasis multitubular tipo trellis', 'Gráficos KRT'],
    },
    {
      id: 'moto-05',
      brand: 'Suzuki',
      model: 'Gixxer 150 Fi ABS',
      displacement: '155 cc',
      category: 'Urbana',
      price: 11400000,
      stock: 7,
      features: ['Tecnología SEP', 'Freno de disco delantero ABS', 'Tablero digital'],
    },
    {
      id: 'moto-06',
      brand: 'Honda',
      model: 'CB 190R 2.0',
      displacement: '184 cc',
      category: 'Naked',
      price: 14200000,
      stock: 5,
      features: ['Inyección PGM-FI', 'Horquilla telescópica invertida', 'Tablero LCD'],
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 tracking-tight flex items-center gap-2.5">
          <Bike className="w-6 h-6 text-indigo-400" />
          Catálogo de Motocicletas
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Inventario y fichas técnicas de los modelos disponibles en la sala de ventas.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {motorcycles.map((moto) => (
          <Card key={moto.id} className="flex flex-col justify-between">
            <div>
              <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/30">
                <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
                  {moto.brand}
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  Stock: <strong className="text-slate-200">{moto.stock} u.</strong>
                </span>
              </div>

              <CardContent className="space-y-4 pt-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-100">{moto.model}</h3>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                    <span className="flex items-center gap-1">
                      <Gauge className="w-3 h-3 text-cyan-400" />
                      {moto.displacement}
                    </span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <Shield className="w-3 h-3 text-emerald-400" />
                      {moto.category}
                    </span>
                  </div>
                </div>

                <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                  <div className="text-[11px] uppercase font-semibold text-slate-400 mb-1">
                    Aspectos Destacados
                  </div>
                  {moto.features.map((feat, i) => (
                    <div key={i} className="flex items-center gap-2 text-xs text-slate-300">
                      <Check className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </div>

            <div className="p-4 border-t border-slate-800 bg-slate-950/40 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-slate-400 uppercase font-semibold block">
                  Precio Base
                </span>
                <span className="text-base font-bold text-amber-400 font-mono">
                  {formatCurrency(moto.price)}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
