[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:ja"="新潟県"]->.inner;
(
  nwr["leisure"~"garden"](area.inner)(area.outer);
);
out geom;
