[out:json][timeout:30];
area["name:en"="Fukuoka"][boundary=administrative]->.outer;
area["name:en"="Fukuoka"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
