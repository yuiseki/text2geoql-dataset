[out:json][timeout:30];
area["name:zh"="南山区"]->.outer;
area["name:en"="Nanshan District"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
