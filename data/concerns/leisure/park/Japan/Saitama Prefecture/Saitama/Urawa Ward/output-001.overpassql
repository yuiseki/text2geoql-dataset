[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Urawa Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
