[out:json][timeout:30000];
area["name:en"="Nepal"]->.outer;
area["name:en"="Karnali Province"]->.inner;
(
  relation["boundary"="administrative"]["name:en"="Jajarkot"](area.inner)(area.outer);
);
out geom;
