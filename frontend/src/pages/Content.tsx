import { useState, useEffect, useRef } from "react";
// import { getOrders } from "../api/orders";
import type { Order } from "../types/Order";

const OrdersPage = () => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [search, setSearch] = useState<string>("");
  const [debouncedSearch, setDebouncedSearch] = useState<string>("");
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dummyOrders: Order[] = [
    {
      id: 1,
      status: "pending",
      total_amount: 129.97,
      created_at: "2025-07-30T14:12:00Z",
      updated_at: "2025-07-31T09:45:00Z",
      items: [
        {
          id: 101,
          stock_item_id: 201,
          name: "Wireless Mouse",
          quantity: 1,
          unit_price: 29.99,
          total_price: 29.99,
        },
        {
          id: 102,
          stock_item_id: 202,
          name: "Mechanical Keyboard",
          quantity: 1,
          unit_price: 99.98,
          total_price: 99.98,
        },
      ],
    },
    {
      id: 2,
      status: "shipped",
      total_amount: 59.98,
      created_at: "2025-07-25T11:00:00Z",
      updated_at: "2025-07-26T16:23:00Z",
      items: [
        {
          id: 103,
          stock_item_id: 203,
          name: "USB-C Charger",
          quantity: 2,
          unit_price: 29.99,
          total_price: 59.98,
        },
      ],
    },
    {
      id: 3,
      status: "delivered",
      total_amount: 199.95,
      created_at: "2025-07-20T08:30:00Z",
      updated_at: "2025-07-22T14:00:00Z",
      items: [
        {
          id: 104,
          stock_item_id: 204,
          name: "HD Monitor",
          quantity: 1,
          unit_price: 199.95,
          total_price: 199.95,
        },
      ],
    },
  ];

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = dummyOrders;
      setOrders(data);
      if (data.length > 0 && selected === null) setSelected(data[0].id);
    } catch (error: unknown) {
      setError(
        error instanceof Error ? error.message : "Failed to fetch orders"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setDebouncedSearch(search);
    }, 400);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search]);

  const filteredOrders = orders.filter(
    (order) =>
      !debouncedSearch ||
      order.id.toString().includes(debouncedSearch) ||
      (order.items &&
        order.items.some((item) =>
          item.name.toLowerCase().includes(debouncedSearch.toLowerCase())
        ))
  );

  const selectedOrder =
    filteredOrders.find((o) => o.id === selected) || filteredOrders[0];

  return (
    <div
      style={{
        display: "flex",
        height: "calc(100vh - 80px)",
        background: "#f7f8fa",
      }}
    >
      {/* Sidebar */}
      <div
        style={{
          width: 320,
          background: "#fff",
          borderRight: "1px solid #eee",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div
          style={{
            padding: 20,
            borderBottom: "1px solid #eee",
            background: "#fff",
          }}
        >
          <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            <input
              type="text"
              placeholder="Search orders..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                padding: 10,
                borderRadius: 6,
                flex: 1,
                color: "#000",
                border: "1px solid #ddd",
                fontSize: 16,
                background: "#fff",
              }}
            />
          </div>
        </div>
        <div style={{ flex: 1, overflowY: "auto" }}>
          {loading ? (
            <div style={{ textAlign: "center", margin: 40 }}>
              <h2>Loading...</h2>
            </div>
          ) : error ? (
            <div style={{ textAlign: "center", color: "red", margin: 40 }}>
              <h2>{error}</h2>
            </div>
          ) : filteredOrders.length === 0 ? (
            <div style={{ textAlign: "center", margin: 40 }}>
              <h2>No Orders</h2>
            </div>
          ) : (
            <ul style={{ listStyle: "none", margin: 0, padding: 0 }}>
              {filteredOrders.map((order) => (
                <li
                  key={order.id}
                  onClick={() => setSelected(order.id)}
                  style={{
                    padding: "16px 20px",
                    borderBottom: "1px solid #f0f0f0",
                    background: selected === order.id ? "#e9f2ff" : undefined,
                    cursor: "pointer",
                    fontWeight: selected === order.id ? 700 : 500,
                    color: selected === order.id ? "#007bff" : "#222",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                    }}
                  >
                    <span>#{order.id}</span>
                    <span style={{ fontSize: 13, color: "#888" }}>
                      {order.status}
                    </span>
                  </div>
                  <div style={{ fontSize: 13, color: "#888", marginTop: 2 }}>
                    Total: ${order.total_amount.toFixed(2)}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      {/* Main Details Panel */}
      <div
        style={{
          flex: 1,
          background: "#f7f8fa",
          padding: 40,
          overflowY: "auto",
        }}
      >
        {selectedOrder ? (
          <div
            style={{
              background: "#fff",
              borderRadius: 10,
              boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              padding: 32,
              minHeight: 300,
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: 24,
              }}
            >
              <h2 style={{ fontWeight: 700, fontSize: 28, margin: 0 }}>
                Order #{selectedOrder.id}
              </h2>
              <span style={{ fontWeight: 600, color: "#007bff", fontSize: 18 }}>
                {selectedOrder.status}
              </span>
            </div>
            <div style={{ display: "flex", gap: 40, marginBottom: 24 }}>
              <div>
                <div style={{ fontSize: 15, color: "#888" }}>Created</div>
                <div style={{ fontWeight: 600 }}>
                  {new Date(selectedOrder.created_at).toLocaleString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 15, color: "#888" }}>Updated</div>
                <div style={{ fontWeight: 600 }}>
                  {new Date(selectedOrder.updated_at).toLocaleString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: 15, color: "#888" }}>Total</div>
                <div style={{ fontWeight: 600 }}>
                  ${selectedOrder.total_amount.toFixed(2)}
                </div>
              </div>
            </div>
            <div>
              <h4 style={{ fontWeight: 600, marginBottom: 12 }}>Order Items</h4>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr>
                    <th
                      style={{
                        padding: 8,
                        textAlign: "left",
                        color: "#888",
                        fontWeight: 600,
                      }}
                    >
                      Name
                    </th>
                    <th
                      style={{
                        padding: 8,
                        textAlign: "left",
                        color: "#888",
                        fontWeight: 600,
                      }}
                    >
                      Quantity
                    </th>
                    <th
                      style={{
                        padding: 8,
                        textAlign: "left",
                        color: "#888",
                        fontWeight: 600,
                      }}
                    >
                      Unit Price
                    </th>
                    <th
                      style={{
                        padding: 8,
                        textAlign: "left",
                        color: "#888",
                        fontWeight: 600,
                      }}
                    >
                      Total Price
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrder.items.map((item) => (
                    <tr key={item.id}>
                      <td style={{ padding: 8 }}>{item.name}</td>
                      <td style={{ padding: 8 }}>{item.quantity}</td>
                      <td style={{ padding: 8 }}>
                        ${item.unit_price.toFixed(2)}
                      </td>
                      <td style={{ padding: 8 }}>
                        ${item.total_price.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
};

export default OrdersPage;
