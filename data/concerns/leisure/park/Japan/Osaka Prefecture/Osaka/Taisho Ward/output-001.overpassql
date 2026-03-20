[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Taisho Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
