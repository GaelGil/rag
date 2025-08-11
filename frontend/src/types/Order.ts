// movie type for declaring var types
export type OrderItem = {
  id: number;
  stock_item_id: number;
  name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
};

export type Order = {
  id: number;
  status: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
};

// moviecardProps type for declaring var types
export type OrderProps = {
  order: Order;
};
