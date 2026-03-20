[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Shimogyo Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
