[out:json][timeout:30];
area["name:en"="Kobe"][boundary=administrative]->.outer;
area["name:en"="Hyogo Prefecture"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
