const CFG = window.APP_CONFIG;

const elToast = document.getElementById("toast");
function toast(msg) {
  elToast.textContent = msg;
  elToast.classList.add("show");
  setTimeout(() => elToast.classList.remove("show"), 3200);
}

function qs(sel){ return document.querySelector(sel); }

async function apiPost(url, body){
  const r = await fetch(url, {
    method:"POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify(body)
  });
  if(!r.ok){
    const t = await r.text();
    throw new Error(t || "Error en request");
  }
  return r.json();
}

function updateTokenUI(){
  const token = localStorage.getItem("token");
  const badge = qs("#tokenStatus");
  const btnGo = qs("#btnGoApp");
  if(token){
    badge.textContent = "Token: SI ";
    btnGo.disabled = false;
  }else{
    badge.textContent = "Token: NO";
    btnGo.disabled = true;
  }
}

function bindRegister(){
  qs("#formRegister").addEventListener("submit", async (ev)=>{
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const body = Object.fromEntries(fd.entries());

    try{
      await apiPost(`${CFG.authUrl}/auth/register`, body);
      toast("Usuario creado ");
      ev.target.reset();
    }catch(e){
      toast("Error registro: " + e.message);
    }
  });
}

function bindLogin(){
  qs("#formLogin").addEventListener("submit", async (ev)=>{
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const body = Object.fromEntries(fd.entries());

    try{
      await apiPost(`${CFG.authUrl}/auth/login`, body);
      toast("Credenciales OK  Ahora pide OTP");
    }catch(e){
      toast("Error login: " + e.message);
    }
  });
}

function bindOtp(){
  qs("#formOtpRequest").addEventListener("submit", async (ev)=>{
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const body = Object.fromEntries(fd.entries());

    try{
      const res = await apiPost(`${CFG.authUrl}/auth/request-otp`, body);
      qs("#otpDemo").textContent = res.demo_code ?? "—";
      toast("OTP generado  (válido 4 minutos)");
    }catch(e){
      toast("Error OTP: " + e.message);
    }
  });

  qs("#formOtpVerify").addEventListener("submit", async (ev)=>{
    ev.preventDefault();
    const fd = new FormData(ev.target);
    const body = Object.fromEntries(fd.entries());

    try{
      const res = await apiPost(`${CFG.authUrl}/auth/verify-otp`, body);
      localStorage.setItem("token", res.token);
      updateTokenUI();
      toast("Token guardado  Ya puedes usar el sistema");
      ev.target.reset();
    }catch(e){
      toast("Error verificar OTP: " + e.message);
    }
  });
}

function bindActions(){
  qs("#btnGoApp").addEventListener("click", ()=>{
    window.location.href = CFG.appUrl;
  });

  qs("#btnLogout").addEventListener("click", ()=>{
    localStorage.removeItem("token");
    updateTokenUI();
    toast("Sesión cerrada ");
  });
}

(async function init(){
  updateTokenUI();
  bindRegister();
  bindLogin();
  bindOtp();
  bindActions();
})();
