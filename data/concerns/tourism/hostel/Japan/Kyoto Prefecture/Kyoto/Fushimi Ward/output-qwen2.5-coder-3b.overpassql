[out:json][timeout:30];
area["name:en"="Kyoto"][boundary=administrative]->.outer;
area["name:en"="Kyoto Prefecture"]->.inner;
(
  nwr["tourism"="hostel"](area.inner)(area.outer);
);
out geom;
