[out:json][timeout:30];
area["name:en"="Shenshan Special Cooperation Zone"]->.outer;
area["name:en"="Shenzhen"]->.inner;
(
  nwr["leisure"~"garden"](area.inner)(area.outer);
);
out geom;
