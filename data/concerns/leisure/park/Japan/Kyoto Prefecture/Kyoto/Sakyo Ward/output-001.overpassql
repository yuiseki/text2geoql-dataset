[out:json][timeout:30000];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Sakyo Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
