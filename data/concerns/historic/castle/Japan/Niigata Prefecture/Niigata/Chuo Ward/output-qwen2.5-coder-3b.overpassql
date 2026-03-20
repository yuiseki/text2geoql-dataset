[out:json][timeout:30];
area["name:ja"="新潟県"]->.outer;
area["name:en"="Niigata Prefecture"]->.inner;
(
  nwr["building"="castle"](area.inner)(area.outer);
);
out geom;
