[out:json][timeout:30];
area["name:zh"="南山区"]->.outer;
area["name:en"="Nanshan District"]->.inner;
(
  nwr["building"~"temple"](area.inner)(area.outer);
);
out geom;
