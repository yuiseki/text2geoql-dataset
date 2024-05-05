[out:json][timeout:30000];
area["name:en"="Osaka"]->.outer;
area["name:en"="Konohana Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
