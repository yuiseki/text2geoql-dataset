[out:json][timeout:30];
area["name:en"="Saitama Prefecture"]->.outer;
area["name:ja"="埼玉県"]->.inner;
(
  nwr["leisure"~"garden"](area.inner)(area.outer);
);
out geom;
