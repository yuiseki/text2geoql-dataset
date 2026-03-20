[out:json][timeout:30];
area["name:en"="Niigata"][boundary=administrative]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;
