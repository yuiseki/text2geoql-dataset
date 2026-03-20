[out:json][timeout:30];
area["name:zh"="光明区"]->.outer;
area["name:en"="Guangming District"]->.inner;
(
  nwr["amenity"="cafe"](area.inner)(area.outer);
);
out geom;
