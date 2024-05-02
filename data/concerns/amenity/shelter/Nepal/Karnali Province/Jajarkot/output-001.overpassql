[out:json][timeout:30000];
area["name:en"="Nepal"]->.outer;
area["name:en"="Karnali Province"]->.inner;
area["name:en"="Jajarkot"]->.inner2;
(
  nwr["amenity"="shelter"](area.inner2)(area.inner)(area.outer);
  nwr["amenity"="refugee_site"](area.inner2)(area.inner)(area.outer);
);
out geom;
