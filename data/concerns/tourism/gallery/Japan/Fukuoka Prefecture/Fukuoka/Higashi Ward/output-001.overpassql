[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Higashi Ward"]->.inner;
(
  nwr["tourism"="gallery"](area.inner)(area.outer);
);
out geom;
