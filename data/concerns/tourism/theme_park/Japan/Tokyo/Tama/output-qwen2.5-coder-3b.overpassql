[out:json][timeout:30];
area["name:en"="Tokyo"]->.outer;
area["name:en"="Tama"]->.inner;
(
  nwr["tourism"="theme_park"](area.inner)(area.outer);
);
out geom;
