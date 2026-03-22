[out:json][timeout:30];
area["name:en"="Miyagi Prefecture"]->.outer;
area["name:en"="Sendai"]->.inner;
(
  nwr["tourism"="hotel"](area.inner)(area.outer);
);
out geom;