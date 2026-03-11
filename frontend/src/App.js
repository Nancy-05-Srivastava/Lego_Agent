import { useState } from "react";

function App() {
  const [showForm, setShowForm] = useState(false);
  const [repo, setRepo] = useState("");
  const [code, setCode] = useState("");
  const [overview, setOverview] = useState("");
  const [repos, setRepos] = useState([]);
  // const [repoResult, setRepoResult] = useState(null);
  const [codeResult, setCodeResult] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [ , setStep] = useState(1);

  // STEP 1 - Repo Discovery
  const analyzeRepo = async () => {
    const res = await fetch("https://lego-ai-backend.onrender.com/api/discover", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        repo_url: repo
      })
    });

    const data = await res.json();

    setRepos(data.similar_repositories);
    setStep(2);
  };

  // STEP 2 - Code Optimizer
  const optimizeCode = async () => {
    const res = await fetch("https://lego-ai-backend.onrender.com/api/optimize-code", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        code: code
      })
    });

    const data = await res.json();

    setCodeResult(data);
    setStep(3);
  };

  // STEP 3 - Opportunity Finder
  const findOpportunities = async () => {
    const res = await fetch("https://lego-ai-backend.onrender.com/api/find-opportunities", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        idea: overview
      })
    });

    const data = await res.json();

    setOpportunities(data.opportunities);
  };

  // LEGO Brick Component
  const LegoBrick = ({ color, darkColor, studs, size, rotation, top, left, right, bottom, delay = 0 }) => (
    <div style={{
      position: "absolute",
      top, left, right, bottom,
      width: size === "large" ? "120px" : size === "small" ? "70px" : "95px",
      height: size === "large" ? "85px" : size === "small" ? "50px" : "65px",
      background: color,
      borderRadius: size === "large" ? "12px" : size === "small" ? "7px" : "10px",
      boxShadow: `0 ${size === "large" ? "12px" : size === "small" ? "7px" : "10px"} 0 ${darkColor}, 0 ${size === "large" ? "18px" : size === "small" ? "10px" : "15px"} 30px rgba(0,0,0,0.3)`,
      transform: `rotate(${rotation}deg)`,
      animation: `float ${5 + delay}s ease-in-out infinite ${delay}s`,
      zIndex: 1
    }}>
      <div style={{ display: "flex", justifyContent: "space-evenly", padding: size === "large" ? "12px 10px" : size === "small" ? "7px 5px" : "10px 8px" }}>
        {[...Array(studs)].map((_, i) => (
          <div key={i} style={{
            width: size === "large" ? "18px" : size === "small" ? "12px" : "16px",
            height: size === "large" ? "18px" : size === "small" ? "12px" : "16px",
            background: darkColor,
            borderRadius: "50%",
            boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3), 0 3px 8px rgba(0,0,0,0.4)"
          }}></div>
        ))}
      </div>
    </div>
  );

  // LEGO Tower Component
  const LegoTower = ({ left, right, bottom, colors }) => (
    <div style={{ position: "absolute", left, right, bottom, zIndex: 1 }}>
      {colors.map((colorSet, i) => (
        <div key={i} style={{
          width: "80px",
          height: "50px",
          background: colorSet.color,
          borderRadius: "8px",
          boxShadow: `0 8px 0 ${colorSet.dark}`,
          marginBottom: i === colors.length - 1 ? "0" : "-8px",
          position: "relative"
        }}>
          <div style={{ display: "flex", justifyContent: "space-evenly", padding: "8px 6px" }}>
            {[1,2,3,4].map(j => (
              <div key={j} style={{
                width: "12px",
                height: "12px",
                background: colorSet.dark,
                borderRadius: "50%",
                boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
              }}></div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  if (!showForm) {
    return (
      <div style={{
        minHeight: "100vh",
        background: "#F5F5F5",
        backgroundImage: `radial-gradient(circle, #D1D5DB 10%, transparent 10%)`,
        backgroundSize: "40px 40px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Arial Black', sans-serif",
        position: "relative",
        overflow: "hidden"
      }}>
        <style>
          {`
            @keyframes float {
              0%, 100% { transform: translateY(0) rotate(var(--rotate, 0deg)); }
              50% { transform: translateY(-25px) rotate(var(--rotate, 0deg)); }
            }
          `}
        </style>

        {/* Multiple Floating LEGO Bricks - Classic Colors Only */}
        <LegoBrick color="#E63946" darkColor="#B71C1C" studs={4} size="medium" rotation={-12} top="8%" left="8%" delay={0} />
        <LegoBrick color="#0055BF" darkColor="#003D8F" studs={3} size="small" rotation={18} top="12%" right="12%" delay={1} />
        <LegoBrick color="#00A550" darkColor="#007A3D" studs={5} size="large" rotation={8} bottom="15%" left="10%" delay={2} />
        <LegoBrick color="#FFED00" darkColor="#CCB800" studs={3} size="small" rotation={-15} bottom="20%" right="15%" delay={1.5} />
        <LegoBrick color="#FF6B35" darkColor="#CC5428" studs={4} size="medium" rotation={-20} top="25%" left="20%" delay={2.5} />
        <LegoBrick color="#E63946" darkColor="#B71C1C" studs={2} size="small" rotation={25} top="40%" right="8%" delay={3} />
        <LegoBrick color="#0055BF" darkColor="#003D8F" studs={4} size="medium" rotation={-8} bottom="35%" left="5%" delay={1.8} />
        <LegoBrick color="#00A550" darkColor="#007A3D" studs={6} size="large" rotation={12} top="60%" left="15%" delay={2.2} />
        <LegoBrick color="#FFED00" darkColor="#CCB800" studs={3} size="small" rotation={-18} bottom="8%" left="25%" delay={3.5} />
        <LegoBrick color="#FF6B35" darkColor="#CC5428" studs={4} size="medium" rotation={15} top="70%" right="20%" delay={1.2} />

        {/* LEGO Towers - Classic Colors Only */}
        <LegoTower 
          left="5%" 
          bottom="5%" 
          colors={[

            { color: "#E63946", dark: "#B71C1C" },
            { color: "#0055BF", dark: "#003D8F" },
            { color: "#FFED00", dark: "#CCB800" }
          ]} 
        />
        
        <LegoTower 
          right="8%" 
          bottom="8%" 
          colors={[
            { color: "#00A550", dark: "#007A3D" },
            { color: "#FF6B35", dark: "#CC5428" },
            { color: "#0055BF", dark: "#003D8F" },
            { color: "#E63946", dark: "#B71C1C" }
          ]} 
        />

        <LegoTower 
          left="25%" 
          bottom="3%" 
          colors={[
            { color: "#FFED00", dark: "#CCB800" },
            { color: "#00A550", dark: "#007A3D" }
          ]} 
        />

        <LegoTower 
          right="25%" 
          bottom="5%" 
          colors={[
            { color: "#FF6B35", dark: "#CC5428" },
            { color: "#E63946", dark: "#B71C1C" },
            { color: "#0055BF", dark: "#003D8F" }
          ]} 
        />

        {/* LEGO Wall Structure - Classic Colors Only */}
        <div style={{
          position: "absolute",
          top: "50%",
          left: "2%",
          transform: "translateY(-50%)",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          zIndex: 1
        }}>
          {[
            { color: "#E63946", dark: "#B71C1C", width: "90px" },
            { color: "#FFED00", dark: "#CCB800", width: "75px" },
            { color: "#0055BF", dark: "#003D8F", width: "90px" },
            { color: "#00A550", dark: "#007A3D", width: "60px" }
          ].map((brick, i) => (
            <div key={i} style={{
              width: brick.width,
              height: "45px",
              background: brick.color,
              borderRadius: "6px",
              boxShadow: `0 6px 0 ${brick.dark}`,
              marginLeft: i % 2 === 0 ? "0" : "20px"
            }}>
              <div style={{ display: "flex", justifyContent: "space-evenly", padding: "6px 5px" }}>
                {[1,2,3].map(j => (
                  <div key={j} style={{
                    width: "10px",
                    height: "10px",
                    background: brick.dark,
                    borderRadius: "50%",
                    boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
                  }}></div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* LEGO Wall Structure Right - Classic Colors Only */}
        <div style={{
          position: "absolute",
          top: "50%",
          right: "2%",
          transform: "translateY(-50%)",
          display: "flex",
          flexDirection: "column",
          gap: "10px",
          zIndex: 1
        }}>
          {[
            { color: "#FF6B35", dark: "#CC5428", width: "85px" },
            { color: "#0055BF", dark: "#003D8F", width: "70px" },
            { color: "#00A550", dark: "#007A3D", width: "85px" },
            { color: "#FFED00", dark: "#CCB800", width: "65px" }
          ].map((brick, i) => (
            <div key={i} style={{
              width: brick.width,
              height: "45px",
              background: brick.color,
              borderRadius: "6px",
              boxShadow: `0 6px 0 ${brick.dark}`,
              marginLeft: i % 2 === 0 ? "20px" : "0"
            }}>
              <div style={{ display: "flex", justifyContent: "space-evenly", padding: "6px 5px" }}>
                {[1,2,3].map(j => (
                  <div key={j} style={{
                    width: "10px",
                    height: "10px",
                    background: brick.dark,
                    borderRadius: "50%",
                    boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
                  }}></div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div style={{
          textAlign: "center",
          zIndex: 10,
          background: "white",
          padding: "60px 80px",
          borderRadius: "30px",
          boxShadow: "0 30px 0 #E5E7EB, 0 35px 60px rgba(0,0,0,0.2)",
          border: "8px solid #0055BF"
        }}>
          <h1 style={{
            fontSize: "64px",
            fontWeight: "900",
            color: "#E63946",
            textShadow: "4px 4px 0 #0055BF",
            marginBottom: "15px",
            letterSpacing: "3px",
            textTransform: "uppercase"
          }}>🧱 LEGO AI</h1>
          
          <p style={{
            fontSize: "20px",
            color: "#6B7280",
            marginBottom: "50px",
            fontWeight: "700",
            textTransform: "uppercase",
            letterSpacing: "2px"
          }}>Build Amazing Projects, Block by Block</p>

          <button onClick={() => setShowForm(true)} style={{
            padding: "25px 70px",
            fontSize: "24px",
            fontWeight: "900",
            background: "#E63946",
            color: "white",
            border: "none",
            borderRadius: "15px",
            cursor: "pointer",
            boxShadow: "0 12px 0 #B71C1C, 0 15px 35px rgba(230, 57, 70, 0.4)",
            transition: "all 0.15s",
            textTransform: "uppercase",
            letterSpacing: "2px",
            position: "relative",
            overflow: "hidden"
          }}
          onMouseEnter={(e) => {
            e.target.style.transform = "translateY(-6px)";
            e.target.style.boxShadow = "0 18px 0 #B71C1C, 0 22px 45px rgba(230, 57, 70, 0.5)";
          }}
          onMouseLeave={(e) => {
            e.target.style.transform = "translateY(0)";
            e.target.style.boxShadow = "0 12px 0 #B71C1C, 0 15px 35px rgba(230, 57, 70, 0.4)";
          }}
          onMouseDown={(e) => {
            e.target.style.transform = "translateY(6px)";
            e.target.style.boxShadow = "0 6px 0 #B71C1C, 0 8px 20px rgba(230, 57, 70, 0.3)";
          }}
          onMouseUp={(e) => {
            e.target.style.transform = "translateY(-6px)";
            e.target.style.boxShadow = "0 18px 0 #B71C1C, 0 22px 45px rgba(230, 57, 70, 0.5)";
          }}>
            🚀 Start Building
          </button>

          <div style={{
            marginTop: "60px",
            display: "flex",
            gap: "30px",
            justifyContent: "center",
            flexWrap: "wrap"
          }}>
            {[
              { icon: "🎯", text: "Easy", color: "#FFED00", shadow: "#CCB800" },
              { icon: "⚡", text: "Fast", color: "#0055BF", shadow: "#003D8F" },
              { icon: "🎨", text: "Creative", color: "#00A550", shadow: "#007A3D" }
            ].map((feature, i) => (
              <div key={i} style={{
                background: feature.color,
                padding: "25px 35px",
                borderRadius: "15px",
                boxShadow: `0 8px 0 ${feature.shadow}, 0 10px 25px rgba(0,0,0,0.2)`,
                border: "4px solid white",
                minWidth: "140px"
              }}>
                <div style={{ fontSize: "42px", marginBottom: "8px" }}>{feature.icon}</div>
                <div style={{ 
                  color: "white", 
                  fontWeight: "900",
                  fontSize: "18px",
                  textShadow: "2px 2px 0 rgba(0,0,0,0.3)",
                  textTransform: "uppercase"
                }}>{feature.text}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "#F5F5F5",
      backgroundImage: `radial-gradient(circle, #D1D5DB 10%, transparent 10%)`,
      backgroundSize: "40px 40px",
      padding: "40px 20px",
      fontFamily: "'Arial Black', sans-serif",
      position: "relative",
      overflow: "hidden"
    }}>
      <style>
        {`
          @keyframes float {
            0%, 100% { transform: translateY(0) rotate(var(--rotate, 0deg)); }
            50% { transform: translateY(-20px) rotate(var(--rotate, 0deg)); }
          }
        `}
      </style>

      {/* Many More Floating bricks on form page */}
      <LegoBrick color="#E63946" darkColor="#B71C1C" studs={3} size="small" rotation={-10} top="5%" left="5%" delay={0} />
      <LegoBrick color="#0055BF" darkColor="#003D8F" studs={4} size="medium" rotation={15} top="10%" right="8%" delay={1} />
      <LegoBrick color="#00A550" darkColor="#007A3D" studs={5} size="large" rotation={-12} bottom="10%" left="12%" delay={2} />
      <LegoBrick color="#FFED00" darkColor="#CCB800" studs={3} size="small" rotation={20} bottom="15%" right="10%" delay={1.5} />
      <LegoBrick color="#FF6B35" darkColor="#CC5428" studs={2} size="small" rotation={-25} top="15%" left="15%" delay={2.5} />
      <LegoBrick color="#E63946" darkColor="#B71C1C" studs={4} size="medium" rotation={10} top="30%" right="18%" delay={1.8} />
      <LegoBrick color="#0055BF" darkColor="#003D8F" studs={3} size="small" rotation={-15} top="50%" left="8%" delay={3.2} />
      <LegoBrick color="#FFED00" darkColor="#CCB800" studs={5} size="large" rotation={12} bottom="25%" left="18%" delay={2.8} />
      <LegoBrick color="#00A550" darkColor="#007A3D" studs={4} size="medium" rotation={-18} bottom="30%" right="15%" delay={1.3} />
      <LegoBrick color="#FF6B35" darkColor="#CC5428" studs={3} size="small" rotation={22} top="45%" right="5%" delay={2.1} />
      <LegoBrick color="#E63946" darkColor="#B71C1C" studs={2} size="small" rotation={-8} bottom="40%" left="6%" delay={3.5} />
      <LegoBrick color="#0055BF" darkColor="#003D8F" studs={6} size="large" rotation={16} top="65%" left="10%" delay={1.6} />
      
      {/* More towers */}
      <LegoTower 
        left="3%" 
        bottom="5%" 
        colors={[

          { color: "#FFED00", dark: "#CCB800" },
          { color: "#E63946", dark: "#B71C1C" }
        ]} 
      />
      
      <LegoTower 
        right="4%" 
        bottom="3%" 
        colors={[

          { color: "#0055BF", dark: "#003D8F" },
          { color: "#00A550", dark: "#007A3D" },
          { color: "#FF6B35", dark: "#CC5428" }
        ]} 
      />

      <LegoTower 
        left="22%" 
        bottom="8%" 
        colors={[

          { color: "#E63946", dark: "#B71C1C" },
          { color: "#FFED00", dark: "#CCB800" },
          { color: "#0055BF", dark: "#003D8F" }
        ]} 
      />

      <LegoTower 
        right="20%" 
        bottom="6%" 
        colors={[

          { color: "#00A550", dark: "#007A3D" },
          { color: "#FF6B35", dark: "#CC5428" }
        ]} 
      />

      {/* Side walls with more bricks */}
      <div style={{
        position: "absolute",
        top: "35%",
        left: "1%",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        zIndex: 1
      }}>
        {[
          { color: "#FF6B35", dark: "#CC5428", width: "75px" },
          { color: "#FFED00", dark: "#CCB800", width: "85px" },
          { color: "#E63946", dark: "#B71C1C", width: "70px" },
          { color: "#0055BF", dark: "#003D8F", width: "80px" },
          { color: "#00A550", dark: "#007A3D", width: "75px" }
        ].map((brick, i) => (
          <div key={i} style={{
            width: brick.width,
            height: "40px",
            background: brick.color,
            borderRadius: "5px",
            boxShadow: `0 5px 0 ${brick.dark}`,
            marginLeft: i % 2 === 0 ? "0" : "15px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-evenly", padding: "5px 4px" }}>
              {[1,2,3].map(j => (
                <div key={j} style={{
                  width: "9px",
                  height: "9px",
                  background: brick.dark,
                  borderRadius: "50%",
                  boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
                }}></div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        position: "absolute",
        top: "40%",
        right: "1%",
        display: "flex",
        flexDirection: "column",
        gap: "8px",
        zIndex: 1
      }}>
        {[
          { color: "#0055BF", dark: "#003D8F", width: "80px" },
          { color: "#E63946", dark: "#B71C1C", width: "65px" },
          { color: "#00A550", dark: "#007A3D", width: "80px" },
          { color: "#FFED00", dark: "#CCB800", width: "70px" },
          { color: "#FF6B35", dark: "#CC5428", width: "75px" }
        ].map((brick, i) => (
          <div key={i} style={{
            width: brick.width,
            height: "40px",
            background: brick.color,
            borderRadius: "5px",
            boxShadow: `0 5px 0 ${brick.dark}`,
            marginLeft: i % 2 === 0 ? "15px" : "0"
          }}>
            <div style={{ display: "flex", justifyContent: "space-evenly", padding: "5px 4px" }}>
              {[1,2,3].map(j => (
                <div key={j} style={{
                  width: "9px",
                  height: "9px",
                  background: brick.dark,
                  borderRadius: "50%",
                  boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
                }}></div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <button onClick={() => setShowForm(false)} style={{
        position: "fixed",
        top: "25px",
        left: "25px",
        padding: "15px 30px",
        background: "#E63946",
        color: "white",
        border: "none",
        borderRadius: "12px",
        cursor: "pointer",
        fontWeight: "900",
        fontSize: "18px",
        boxShadow: "0 8px 0 #B71C1C",
        transition: "all 0.15s",
        zIndex: 1000,
        textTransform: "uppercase"
      }}
      onMouseDown={(e) => {
        e.target.style.transform = "translateY(4px)";
        e.target.style.boxShadow = "0 4px 0 #B71C1C";
      }}
      onMouseUp={(e) => {
        e.target.style.transform = "translateY(0)";
        e.target.style.boxShadow = "0 8px 0 #B71C1C";
      }}>
        ← Back
      </button>

      <div style={{
        maxWidth: "800px",
        margin: "0 auto",
        background: "white",
        borderRadius: "25px",
        padding: "50px",
        boxShadow: "0 25px 0 #E5E7EB, 0 30px 60px rgba(0,0,0,0.25)",
        border: "8px solid #0055BF",
        position: "relative",
        zIndex: 10
      }}>
        <h1 style={{
          color: "#E63946",
          fontSize: "42px",
          marginBottom: "40px",
          textAlign: "center",
          fontWeight: "900",
          textShadow: "3px 3px 0 #0055BF",
          textTransform: "uppercase",
          letterSpacing: "3px"
        }}>🧱 Build Project</h1>

        <form>
          {/* Repository Brick */}
          <div style={{
            background: "#FFED00",
            padding: "8px",
            borderRadius: "18px",
            marginBottom: "30px",
            boxShadow: "0 10px 0 #CCB800, 0 12px 30px rgba(0,0,0,0.2)",
            border: "5px solid #FFB300"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "center",
              gap: "15px",
              marginBottom: "15px",
              paddingTop: "10px"
            }}>
              {[1,2,3,4,5,6].map(i => (
                <div key={i} style={{
                  width: "18px",
                  height: "18px",
                  background: "#CCB800",
                  borderRadius: "50%",
                  boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3)"
                }}></div>
              ))}
            </div>
            <div style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px"
            }}>
              <label style={{
                display: "block",
                marginBottom: "12px",
                color: "#E63946",
                fontWeight: "900",
                fontSize: "16px",
                textTransform: "uppercase",
                letterSpacing: "1.5px"
              }}>🔗 Repository Link *</label>
              <input
                type="text"
                placeholder="Enter GitHub Repo Link"
                value={repo}
                onChange={(e) => setRepo(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "16px 20px",
                  border: "4px solid #0055BF",
                  borderRadius: "12px",
                  fontSize: "16px",
                  outline: "none",
                  boxSizing: "border-box",
                  fontWeight: "600",
                  boxShadow: "0 6px 0 #003D8F",
                  transition: "all 0.2s",
                  marginBottom: "20px"
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#E63946";
                  e.target.style.boxShadow = "0 6px 0 #B71C1C";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#0055BF";
                  e.target.style.boxShadow = "0 6px 0 #003D8F";
                }}
              />

              <button type="button" onClick={analyzeRepo} style={{
                width: "100%",
                padding: "16px",
                background: "#00A550",
                color: "white",
                border: "none",
                borderRadius: "12px",
                fontSize: "18px",
                fontWeight: "900",
                cursor: "pointer",
                transition: "all 0.15s",
                boxShadow: "0 8px 0 #007A3D",
                textTransform: "uppercase",
                letterSpacing: "2px"
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #007A3D";
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 8px 0 #007A3D";
              }}
              onMouseDown={(e) => {
                e.target.style.transform = "translateY(4px)";
                e.target.style.boxShadow = "0 4px 0 #007A3D";
              }}
              onMouseUp={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #007A3D";
              }}>
                🔍 Analyze Repository
              </button>
            </div>
          </div>

          {/* Similar Repositories Section */}
          {repos.length > 0 && (
            <div style={{ marginBottom: "30px" }}>
              <h2 style={{
                color: "#0055BF",
                fontSize: "28px",
                marginBottom: "25px",
                textAlign: "center",
                fontWeight: "900",
                textShadow: "2px 2px 0 #E63946",
                textTransform: "uppercase",
                letterSpacing: "2px"
              }}>🔍 Similar Repositories</h2>

              {repos.map((r, index) => {
                const colors = [
                  { bg: "#FF6B35", dark: "#CC5428" },
                  { bg: "#0055BF", dark: "#003D8F" },
                  { bg: "#00A550", dark: "#007A3D" },
                  { bg: "#FFED00", dark: "#CCB800" },
                  { bg: "#E63946", dark: "#B71C1C" }
                ];
                const colorSet = colors[index % colors.length];

                return (
                  <div key={index} style={{
                    background: colorSet.bg,
                    padding: "8px",
                    borderRadius: "18px",
                    marginBottom: "20px",
                    boxShadow: `0 8px 0 ${colorSet.dark}, 0 10px 25px rgba(0,0,0,0.2)`,
                    border: "4px solid white"
                  }}>
                    <div style={{
                      display: "flex",
                      justifyContent: "center",
                      gap: "12px",
                      marginBottom: "12px",
                      paddingTop: "8px"
                    }}>
                      {[1,2,3,4].map(i => (
                        <div key={i} style={{
                          width: "14px",
                          height: "14px",
                          background: colorSet.dark,
                          borderRadius: "50%",
                          boxShadow: "inset 0 -2px 0 rgba(0,0,0,0.3)"
                        }}></div>
                      ))}
                    </div>
                    <div style={{
                      background: "white",
                      padding: "20px",
                      borderRadius: "10px"
                    }}>
                      <h3 style={{
                        color: "#E63946",
                        fontSize: "18px",
                        fontWeight: "900",
                        marginBottom: "10px",
                        textTransform: "uppercase",
                        letterSpacing: "1px"
                      }}>{r.name}</h3>
                      
                      <p style={{
                        color: "#4B5563",
                        fontSize: "14px",
                        marginBottom: "12px",
                        lineHeight: "1.5",
                        fontWeight: "600"
                      }}>{r.description}</p>
                      
                      <div style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "15px",
                        marginBottom: "15px"
                      }}>
                        <span style={{
                          background: "#FFED00",
                          color: "#1a1a1a",
                          padding: "6px 12px",
                          borderRadius: "8px",
                          fontWeight: "900",
                          fontSize: "13px",
                          boxShadow: "0 3px 0 #CCB800",
                          border: "2px solid #FFB300"
                        }}>⭐ {r.stars} Stars</span>
                      </div>

                      <a 
                        href={r.url} 
                        target="_blank" 
                        rel="noreferrer"
                        style={{
                          display: "inline-block",
                          padding: "10px 20px",
                          background: "#0055BF",
                          color: "white",
                          textDecoration: "none",
                          borderRadius: "10px",
                          fontWeight: "900",
                          fontSize: "14px",
                          boxShadow: "0 5px 0 #003D8F",
                          transition: "all 0.15s",
                          textTransform: "uppercase",
                          letterSpacing: "1px"
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.transform = "translateY(-2px)";
                          e.target.style.boxShadow = "0 7px 0 #003D8F";
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.transform = "translateY(0)";
                          e.target.style.boxShadow = "0 5px 0 #003D8F";
                        }}
                        onMouseDown={(e) => {
                          e.target.style.transform = "translateY(2px)";
                          e.target.style.boxShadow = "0 3px 0 #003D8F";
                        }}
                        onMouseUp={(e) => {
                          e.target.style.transform = "translateY(-2px)";
                          e.target.style.boxShadow = "0 7px 0 #003D8F";
                        }}
                      >
                        🔗 View Repository
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Code Snippet Brick */}
          <div style={{
            background: "#0055BF",
            padding: "8px",
            borderRadius: "18px",
            marginBottom: "30px",
            boxShadow: "0 10px 0 #003D8F, 0 12px 30px rgba(0,0,0,0.2)",
            border: "5px solid #2563EB"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "center",
              gap: "15px",
              marginBottom: "15px",
              paddingTop: "10px"
            }}>
              {[1,2,3,4,5,6].map(i => (
                <div key={i} style={{
                  width: "18px",
                  height: "18px",
                  background: "#003D8F",
                  borderRadius: "50%",
                  boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3)"
                }}></div>
              ))}
            </div>
            <div style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px"
            }}>
              <label style={{
                display: "block",
                marginBottom: "12px",
                color: "#E63946",
                fontWeight: "900",
                fontSize: "16px",
                textTransform: "uppercase",
                letterSpacing: "1.5px"
              }}>💻 Code Snippet *</label>
              <textarea
                placeholder="Paste your code snippet here"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "16px 20px",
                  border: "4px solid #0055BF",
                  borderRadius: "12px",
                  fontSize: "15px",
                  minHeight: "150px",
                  fontFamily: "'Courier New', monospace",
                  outline: "none",
                  boxSizing: "border-box",
                  resize: "vertical",
                  fontWeight: "500",
                  boxShadow: "0 6px 0 #003D8F",
                  transition: "all 0.2s",
                  marginBottom: "20px"
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#00A550";
                  e.target.style.boxShadow = "0 6px 0 #007A3D";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#0055BF";
                  e.target.style.boxShadow = "0 6px 0 #003D8F";
                }}
              />

              <button type="button" onClick={optimizeCode} style={{
                width: "100%",
                padding: "16px",
                background: "#FF6B35",
                color: "white",
                border: "none",
                borderRadius: "12px",
                fontSize: "18px",
                fontWeight: "900",
                cursor: "pointer",
                transition: "all 0.15s",
                boxShadow: "0 8px 0 #CC5428",
                textTransform: "uppercase",
                letterSpacing: "2px"
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #CC5428";
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 8px 0 #CC5428";
              }}
              onMouseDown={(e) => {
                e.target.style.transform = "translateY(4px)";
                e.target.style.boxShadow = "0 4px 0 #CC5428";
              }}
              onMouseUp={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #CC5428";
              }}>
                ⚡ Optimize Code
              </button>
            </div>
          </div>

          {/* Code Optimizer Results */}
          {codeResult && (
            <div style={{
              background: "#E63946",
              padding: "8px",
              borderRadius: "18px",
              marginBottom: "30px",
              boxShadow: "0 10px 0 #B71C1C, 0 12px 30px rgba(0,0,0,0.2)",
              border: "5px solid #F87171"
            }}>
              <div style={{
                display: "flex",
                justifyContent: "center",
                gap: "15px",
                marginBottom: "15px",
                paddingTop: "10px"
              }}>
                {[1,2,3,4,5,6].map(i => (
                  <div key={i} style={{
                    width: "18px",
                    height: "18px",
                    background: "#B71C1C",
                    borderRadius: "50%",
                    boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3)"
                  }}></div>
                ))}
              </div>
              <div style={{
                background: "white",
                padding: "25px",
                borderRadius: "12px"
              }}>
                <h2 style={{
                  color: "#E63946",
                  fontSize: "24px",
                  marginBottom: "20px",
                  fontWeight: "900",
                  textTransform: "uppercase",
                  letterSpacing: "1.5px"
                }}>💡 Code Suggestions</h2>

                <div style={{ marginBottom: "25px" }}>
                  {codeResult.suggestions && codeResult.suggestions.map((s, i) => (
                    <p key={i} style={{
                      color: "#4B5563",
                      fontSize: "15px",
                      marginBottom: "10px",
                      lineHeight: "1.6",
                      fontWeight: "600",
                      paddingLeft: "20px"
                    }}>• {s}</p>
                  ))}
                </div>

                 

                <h3 style={{
                  color: "#00A550",
                  fontSize: "20px",
                  marginBottom: "15px",
                  fontWeight: "900",
                  textTransform: "uppercase",
                  letterSpacing: "1px"
                }}>✨ Optimized Code</h3>
                <pre style={{
                  background: "#F3F4F6",
                  padding: "15px",
                  borderRadius: "10px",
                  overflow: "auto",
                  fontSize: "14px",
                  fontFamily: "'Courier New', monospace",
                  border: "3px solid #00A550",
                  color: "#1F2937",
                  fontWeight: "600"
                }}>{codeResult.optimized_code}</pre>
              </div>
            </div>
          )}

          {/* Project Overview Brick */}
          <div style={{
            background: "#00A550",
            padding: "8px",
            borderRadius: "18px",
            marginBottom: "35px",
            boxShadow: "0 10px 0 #007A3D, 0 12px 30px rgba(0,0,0,0.2)",
            border: "5px solid #4ADE80"
          }}>
            <div style={{
              display: "flex",
              justifyContent: "center",
              gap: "15px",
              marginBottom: "15px",
              paddingTop: "10px"
            }}>
              {[1,2,3,4,5,6].map(i => (
                <div key={i} style={{
                  width: "18px",
                  height: "18px",
                  background: "#007A3D",
                  borderRadius: "50%",
                  boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3)"
                }}></div>
              ))}
            </div>
            <div style={{
              background: "white",
              padding: "25px",
              borderRadius: "12px"
            }}>
              <label style={{
                display: "block",
                marginBottom: "12px",
                color: "#E63946",
                fontWeight: "900",
                fontSize: "16px",
                textTransform: "uppercase",
                letterSpacing: "1.5px"
              }}>📝 Project Overview *</label>
              <textarea
                placeholder="Describe your project"
                value={overview}
                onChange={(e) => setOverview(e.target.value)}
                required
                style={{
                  width: "100%",
                  padding: "16px 20px",
                  border: "4px solid #0055BF",
                  borderRadius: "12px",
                  fontSize: "15px",
                  minHeight: "150px",
                  outline: "none",
                  boxSizing: "border-box",
                  resize: "vertical",
                  fontWeight: "500",
                  boxShadow: "0 6px 0 #003D8F",
                  transition: "all 0.2s",
                  marginBottom: "20px"
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = "#FFED00";
                  e.target.style.boxShadow = "0 6px 0 #CCB800";
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = "#0055BF";
                  e.target.style.boxShadow = "0 6px 0 #003D8F";
                }}
              />

              <button type="button" onClick={findOpportunities} style={{
                width: "100%",
                padding: "16px",
                background: "#FFED00",
                color: "#1a1a1a",
                border: "none",
                borderRadius: "12px",
                fontSize: "18px",
                fontWeight: "900",
                cursor: "pointer",
                transition: "all 0.15s",
                boxShadow: "0 8px 0 #CCB800",
                textTransform: "uppercase",
                letterSpacing: "2px"
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #CCB800";
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = "translateY(0)";
                e.target.style.boxShadow = "0 8px 0 #CCB800";
              }}
              onMouseDown={(e) => {
                e.target.style.transform = "translateY(4px)";
                e.target.style.boxShadow = "0 4px 0 #CCB800";
              }}
              onMouseUp={(e) => {
                e.target.style.transform = "translateY(-3px)";
                e.target.style.boxShadow = "0 11px 0 #CCB800";
              }}>
                🎯 Find Opportunities
              </button>
            </div>
          </div>

          {/* Opportunities Section */}
          {opportunities.length > 0 && (
            <div style={{
              background: "#FFED00",
              padding: "8px",
              borderRadius: "18px",
              marginBottom: "30px",
              boxShadow: "0 10px 0 #CCB800, 0 12px 30px rgba(0,0,0,0.2)",
              border: "5px solid #FFB300"
            }}>
              <div style={{
                display: "flex",
                justifyContent: "center",
                gap: "15px",
                marginBottom: "15px",
                paddingTop: "10px"
              }}>
                {[1,2,3,4,5,6].map(i => (
                  <div key={i} style={{
                    width: "18px",
                    height: "18px",
                    background: "#CCB800",
                    borderRadius: "50%",
                    boxShadow: "inset 0 -3px 0 rgba(0,0,0,0.3)"
                  }}></div>
                ))}
              </div>
              <div style={{
                background: "white",
                padding: "25px",
                borderRadius: "12px"
              }}>
                <h2 style={{
                  color: "#E63946",
                  fontSize: "28px",
                  marginBottom: "25px",
                  textAlign: "center",
                  fontWeight: "900",
                  textShadow: "2px 2px 0 #0055BF",
                  textTransform: "uppercase",
                  letterSpacing: "2px"
                }}>🎯 Hackathons / Opportunities</h2>

                {opportunities.map((o, i) => (
                  <div key={i} style={{
                    background: "#F3F4F6",
                    padding: "20px",
                    borderRadius: "12px",
                    marginBottom: "20px",
                    border: "4px solid #0055BF",
                    boxShadow: "0 6px 0 #003D8F"
                  }}>
                    <p style={{
                      color: "#E63946",
                      fontSize: "18px",
                      fontWeight: "900",
                      marginBottom: "12px",
                      textTransform: "uppercase",
                      letterSpacing: "1px"
                    }}>{o.title}</p>
                    
                    <a 
                      href={o.link} 
                      target="_blank" 
                      rel="noreferrer"
                      style={{
                        display: "inline-block",
                        color: "#0055BF",
                        fontSize: "15px",
                        fontWeight: "700",
                        textDecoration: "none",
                        padding: "10px 20px",
                        background: "#E0E7FF",
                        borderRadius: "8px",
                        transition: "all 0.2s"
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = "#0055BF";
                        e.target.style.color = "white";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = "#E0E7FF";
                        e.target.style.color = "#0055BF";
                      }}
                    >
                      🔗 {o.link}
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

export default App;
