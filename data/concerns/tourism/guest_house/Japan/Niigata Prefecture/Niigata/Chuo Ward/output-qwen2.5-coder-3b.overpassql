[out:json][timeout:30];
area["name:en"="Niigata"][boundary=administrative]->.outer;
area["name:en"="Niigata"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
