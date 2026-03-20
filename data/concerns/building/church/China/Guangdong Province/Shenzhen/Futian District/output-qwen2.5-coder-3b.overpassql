[out:json][timeout:30];
area["name:zh"="福田区"]->.outer;
area["name:en"="Futian District"]->.inner;
(
  nwr["building"~"church"](area.inner)(area.outer);
);
out geom;
